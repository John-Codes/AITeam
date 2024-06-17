import os
import json
import time
import uuid
from pathlib import Path
from django.http import JsonResponse, StreamingHttpResponse, HttpResponseRedirect
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.views import LoginView, PasswordResetView
from django.urls import reverse_lazy, reverse
from django.views.generic.edit import CreateView 
from django.views import View
from django.contrib.sessions.models import Session
from .forms import * # class to clean an prosces form reset_password
from django.contrib import messages 
from .models import Client as User
from .models import ClienContext, SubscriptionDetail
from django.contrib.auth import logout 
from django.shortcuts import render,redirect, get_object_or_404
from django.template.loader import render_to_string
from AI_Team.Logic.ollama.ollama_json_generator import jsonPageDescriptionOllama
from AI_Team.Logic.Memory import *
from AI_Team.Logic.response_utils import * # IA message render templates method
from AI_Team.Logic.sender_mails import Contac_us_mail, notice_error_forms
from AI_Team.Logic.Data_Saver import DataSaver
from AI_Team.Logic.ollama.ollama_rag_Module import OllamaRag
from AI_Team.Logic.Cancel_Subscription import cancel_subscription
from AI_Team.Logic.Charge_Context import Charge_Context
from AI_Team.Logic.chat_history_endpoint_utils  import validate_request_data, get_chat_history_from_session, get_ai_handler_from_session, update_session_with_chat_history
from AI_Team.Logic.Chat.pdf_handling import *
from AI_Team.Logic.Chat.handle_temporal_rag import process_temp_context_chat
from AI_Team.Logic.AIManager.llm_api_Handler_module import ai_Handler
from AI_Team.Logic.sender_mails import notice_error
from AI_Team.Logic.AI_Instructions.get_ai_instructions import get_instructions
from AI_Team.Logic.Wishper.AudioTextConverter import AudioTextConverter
#from AI_Team.Logic.ollama.ollama_rag_Module import OllamaRag
from .create_paypal import *
from hashids import Hashids
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required

# Stripe using stripe
import stripe
# PayPal
#from paypal.standard.forms import PayPalPaymentsForm
#from paypal.standard.ipn.models import PayPalIPN
from django.dispatch import receiver
#from paypal.standard.ipn.signals import valid_ipn_received

import paypalrestsdk
from django.conf import settings
from AI_Team.Logic.Payments import plans_data
from datetime import datetime, timedelta
#from .models import Current_Plan, PaymentMethod, SubscriptionStatus
from django.utils.translation import gettext as _
stripe.api_key = settings.STRIPE_SECRET_KEY
hashids = Hashids(salt = os.getenv("salt"), min_length=8)

#STRIPE_PUBLIC_KEY': settings.STRIPE_PUBLIC_KEY

# ai-team chat handle events and requests
# SANDBOX MODE
# paypalrestsdk.configure({
#     "mode": "sandbox",  # sandbox or live (production),  # Use 'live' for production
#     "client_id": os.getenv("PCI"),
#     "client_secret": os.getenv("PCS")
# })

# LIVE MODE
paypalrestsdk.configure({
    "mode": "live", 
    "client_id": os.getenv("PCI"),
    "client_secret": os.getenv("PCS")
})

class ChatUIView(View):
    def __init__(self, *args, **kwargs):
        super(ChatUIView, self).__init__(*args, **kwargs)
        self.context_value = None
        self.conversation = Conversation()
        self.stream_calls_methods_dict = {'main': self.conversation.main_query_temp_rag_if_it_exist,
                                        'subscription': self.conversation.stream_chat,
                                        'panel-admin': self.conversation.main_query_perm_rag_if_it_exist,
                                        'default': self.conversation.user_chat_query_existing_perm_rag
                                        }

        
    def get(self, request, *args, **kwargs):
        crhoma_client = self.conversation.ai_handler.ai.chroma_client
        process_temp_context_chat(request, crhoma_client)
        
        #delete_collection_by_name
        valid_contexts = ["main", "subscription", "panel-admin"]
        titles = {"main": [_('EFEXZIUM'), _('AI Team Chat')], "subscription": [_('Subscriptions'), _('AI Team Subscriptions')], "panel-admin": [_('Create your own page'), _('AI Team Page Builder')]}
        page_data = DataSaver()
        
        self.context_value = kwargs.get('context', None)
        # obtener instrucciones:
        #context_data_ai = get_instructions(self.context_value)
        # iniciar el rag dado el path donde esta el contexto o las instrucciones para la IA
        #
        # Si el contexto es uno de los personalizados
        
        if self.context_value not in valid_contexts:
            site_exists = page_data.check_site(check_context=self.context_value)
            if not site_exists:
                return redirect('/chat/main')
            # Extraer el valor real del context
            context_filename = "memory-AI-with-" + self.context_value.split('Uptc%3Fto=')[-1].rstrip('$')
            # obten el data_dict y el error si hay error enviamos email con notice_error
            data_dict, error = page_data.json_to_dict(context_filename)
            if data_dict:
                context = {
                    'website_data': data_dict,
                    'context_value': self.context_value,
                }
            # si hay error enviamos email con notice_error
            elif error:
                # parametro de notice error asunto = Error al cargar chat perzonalizado del usuario con filename = context_filename mensaje = error (en ingles)
                notice_error(f"Error charging custom chat page with filename: {context_filename} ", error)
            return render(request, 'ai-team-customize.html', context)

        # if the context is pre defined in a file
        else:
            user_id = request.user.id
            site_exists = page_data.check_site(user_id)

            # Si el usuario está autenticado, obtenemos la URL del sitio del usuario.
            if request.user.is_authenticated:
                hashed_id = hashids.encode(user_id)
                user_page = f'Uptc%3Fto={hashed_id}$'
                url = reverse('ai-team', kwargs={'context': user_page})
                context_filename = "memory-AI-with-" + hashed_id
                data_dict, error = page_data.json_to_dict(context_filename)
                
                context = {
                    'title': titles[self.context_value][0],
                    'header': titles[self.context_value][1],
                    'context_value': self.context_value,
                    'valid_contexts': valid_contexts,
                    'site_exists': site_exists,
                }
                
                if site_exists:
                    context['my_site_IA']= url
                    context['my_site_title']= data_dict['header']
            else:
                context = {
                    'title': titles[self.context_value][0],
                    'header': titles[self.context_value][1],
                    'context_value': self.context_value,
                    'valid_contexts': valid_contexts
                
                }

            return render(request, 'ai-team.html', context)

    @method_decorator(csrf_exempt)
    def post(self, request, *args, **kwargs):
        # Preparación de datos de la solicitu
        self.context_value = kwargs.get('context')
        method = request.POST.get('action', None)
        if method is None:
            data = json.loads(request.body)
            method = data.get('action', None)
        # use the creator_rag function when endpoint in data == 'creator_rag'    
        
        if method == 'create-temp-rag':
            return self.conversation.temp_rag_creator(request)

        elif method == 'create-perm-rag':
            return self.conversation.permanent_rag_creator(request)

        elif method == 'call-stream-ia':
            if self.context_value in self.stream_calls_methods_dict:
            # Call the corresponding method dynamically
                return self.stream_calls_methods_dict[self.context_value](request)
            else:
                return self.stream_calls_methods_dict['default'](request)
        else:
            return JsonResponse({'error': 'Invalid request method'}, status=400)
      

    def send_email(self, user_message):
        if ('@' and '.') in user_message:
            Contac_us_mail(user_message)  

@csrf_exempt
def handle_template_messages(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        template_name = data.get('template_name', None)
        print(template_name)
        if template_name:
            response_data = {}
            response_data['html'] = render_to_string(f'chat_messages/{template_name}.html')
            if template_name == "contact_us":
                request.session['awaiting_contact_email'] = True    
            time.sleep(2)
            return JsonResponse(response_data)
        else:
            return JsonResponse({"error": "template_name not provided"}, status=400)

@csrf_exempt
def send_contact_email(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        email = data.get('email', None)
        if email:
            if '@' in email and '.' in email:
            # Aquí puedes usar tu lógica para enviar el correo
                Contac_us_mail(email)
                message = _('Thank you! We will contact you soon.')
            else:
                # mensaje en inglés que informa de un falle y le pide al usuario que de click en Contact Us otra vez
                message = _('Failed to send your email. Please click on Contact Us and try again.')
            message_html =render_to_string(f'chat_messages/ia_message.html', {'message': message})
            return JsonResponse({"success": "Email sent successfully", "message": message_html})
        else:
            return JsonResponse({"error": "Email not provided"}, status=400)
    else:
        return JsonResponse({"error": "Invalid request method"}, status=400)


# create a method to handle a cancel subscription post request
def handle_cancel_subscription(request):
    if request.method == 'POST':
        # Recoger las respuestas del formulario
        reason = request.POST.get('reason', '')
        improvement = request.POST.get('improvement', '')
        # Concatenar las respuestas en una variable de texto con saltos de línea
        cancel_status = cancel_subscription(request,request.user.order_id)
        subject = F'Subscription Cancellation by User {request.user.email}'
        user_feedback = f"Reason for cancellation:\n{reason}\nSuggestions for improvement:\n{improvement} \n Status of cancellation: {cancel_status}"   
        notice_error(subject, user_feedback)
        # Aquí llamarías a la función que maneja la cancelación de la suscripción
        
        return HttpResponseRedirect(reverse('ai-team', kwargs={'context': 'subscription'}))
    else:
        # Si no es un POST, simplemente renderiza la página con el formulario
        return JsonResponse({'error': 'Invalid request method'}, status=400)

def handle_interaction_user_messages(request):
    print('body request',request.body)
    if request.method == 'POST':
        data = json.loads(request.body)
        message = data.get('message')
        action = data.get('action')
        url = data.get('url')
        if not request.user.is_authenticated:
            # Render the login form or any other HTML you want to show when the user is not authenticated
            html_content = render_to_string('chat_messages/create_acccount_message.html')
            return JsonResponse({'not_authenticated': True, 'html': html_content})
        else:
            user_email = request.user.email
            notice_error(subject=f'An user {user_email} {action} the message in chat {url} ', message=f'Message: {message}')
        # Handle the interaction (like or dislike) here
        # For example, you can save the interaction to the database or perform any other action

        return JsonResponse({'success': True, 'message': f'{action} recorded successfully'})
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=400)


class Conversation():
    def __init__(self):
        self.ai_handler = ai_Handler()
        self.chat_history = Chat_history()
        self.stream_ollama = OllamaRag()
        self.json_page = DataSaver()

    
    @method_decorator(csrf_exempt)
    def stream_chat(self,request):
        # ya no es necesario ai_Handler para eso es el endpoint
        #ai = ai_Handler()
        if request.method == 'POST':        
            chat_ollama = OllamaRag()
            data = json.loads(request.body)
            current_chat = data.get('current_chat')
            list_messages = data.get('list_messages')#self.reset_chat_history(data)
            list_messages = self.ai_handler.load_static_messages(list_messages, current_chat)
            
            #list_messages = self.ai_handler.update_messages(last_ia_response, message)
            # CLient Side add ia response
            return StreamingHttpResponse(chat_ollama.stream_query_ollama(list_messages), content_type='text/event-stream')
        else:
            return JsonResponse({'error': 'Invalid request method'}, status=400)
        
    # call this method as endpointd
    
    @method_decorator(csrf_exempt)
    def main_query_temp_rag_if_it_exist(self, request):
        data = json.loads(request.body)
        current_chat = data.get('current_chat')
        # get the list messages
        list_messages = data.get('list_messages')
        # get the last message of the user
        message = list_messages[-1]['content']

        # if there is a temp collection
        if request.session.get('temp_collection_exist', False):
            
            #get the collection by name using the temp_uuid
            collection_name = request.session['temp_collection_exist']['temp_uuid']
            metadata = request.session['temp_collection_exist']['pdf_path']
            collection = self.ai_handler.get_collection_by_name(collection_name)

            # then call ai_handler method: call_ai_temp_rag that returns a formatted prompt with the context
            formatted_prompt = self.ai_handler.query_user_collection_with_chat_context(metadata, message, collection)

            # update the last message with the formatted prompt
            list_messages[-1]['content'] = formatted_prompt
            list_messages = self.ai_handler.load_static_messages(list_messages, 'custom_chat')
        else:
            # if not temp collection then load static messages at the beginning of the list of messages
            list_messages = self.ai_handler.load_static_messages(list_messages, current_chat)

        return StreamingHttpResponse(self.ai_handler.call_ollama_stream(list_messages), content_type='text/event-stream')
        
    
    @method_decorator(csrf_exempt)
    def main_query_perm_rag_if_it_exist(self, request):
        #call reset_chat_history if its necessary
        data = json.loads(request.body)
        current_chat = data.get('current_chat')
        list_messages = data.get('list_messages')
        list_messages = self.ai_handler.load_static_messages(list_messages, current_chat)
        #message = list_messages[-1]['content']
        # if persisted rag exist:
            # 
            # then update_messages
            # and last StreamingHttpResponse with call_ollama_stream
        #if not then call ai_handler llm query no rag

        return StreamingHttpResponse(self.ai_handler.call_ollama_stream(list_messages), content_type='text/event-stream')
    
    # create a method that named user_chat_query_existing_perm_rag and his parameters are the same as main_query_perm_rag_if_it_exist
    def user_chat_query_existing_perm_rag(self, request):
        # que the data with json.loads request.body
        data = json.loads(request.body)
        current_chat = data.get('current_chat')
        list_messages = data.get('list_messages')
        message = list_messages[-1]['content']

        # get the user_id from the current_chat
        user_id = current_chat.split('Uptc%3Fto=')[-1].rstrip('$')
        user_id = hashids.decode(user_id)[0]

        # get the user email from the user_id using the model User
        user_email_page_creator = User.objects.get(id=user_id).email

        # get the collection by name using the email_ user
        collection = self.ai_handler.get_collection_by_name(user_email_page_creator)
        formatted_prompt = self.ai_handler.query_user_collection_with_chat_context(user_email_page_creator ,message, collection)
        list_messages[-1]['content'] = formatted_prompt
        list_messages = self.ai_handler.load_static_messages(list_messages, 'custom_chat')

        return StreamingHttpResponse(self.ai_handler.call_ollama_stream(list_messages), content_type='text/event-stream')
    # only reset chat history
    def reset_chat_history(self, data):
        try:
            validated_data, error_response = validate_request_data(data)
            
            if error_response:
                return error_response
            
            current_chat = validated_data
            
            # set static messages current chat and reset history if the user has changed
            # return list of messages with get_messages method
            history = self.ai_handler.reset_history(current_chat)
            
            return history
    
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON'}, status=400)

    # call this method in ChatUIView POST method
    def temp_rag_creator(self, request):
        if request.method == 'POST':
            context_value = request.POST.get('context_value')
            pdf_file, upload_success = proccess_context_files(request, context_value)
            temp_uuid = str(uuid.uuid4())
            if pdf_file != 'no path' and upload_success:
                
                self.ai_handler.create_collection_rag_with_a_pdf(pdf_file, temp_uuid, permanent=False)
                request.session['temp_collection_exist'] = {'pdf_path': pdf_file, 'temp_uuid': temp_uuid} 
                #delete_temp_pdfs(pdf_file)
                html_message = render_to_string('chat_messages/temp_rag_success.html')
                return JsonResponse({'message': html_message})
            elif pdf_file == 'no path':
                return JsonResponse({'message': 'No path for PDF file', 'upload_success': upload_success})
            else:
                return JsonResponse({'error': 'File processing failed'}, status=400)
        else:
            return JsonResponse({'error': 'Invalid request method'}, status=405)
    
    def permanent_rag_creator(self, request):
        if request.method == 'POST':
            context_value = request.POST.get('context_value')
            pdf_file, upload_success = proccess_context_files(request, context_value)
            if request.user.is_authenticated:
                collection_name = request.user.email
                # hashea el id del usuario con Hashid
                hashed_id = hashids.encode(request.user.id)
                user_page = f'Uptc%3Fto={hashed_id}$'
                # if user has a collection, use upsert method else use create collection
            else:
                return JsonResponse({'error': 'No user authenticated'}, status=400)
            
            if pdf_file != 'no path' and upload_success:
                
                collection =self.ai_handler.create_collection_rag_with_a_pdf(pdf_file, collection_name, permanent=request.user.email)
                create_json = self.create_json_page(request.user.id ,request.user.email,collection=collection)
                #delete_temp_pdfs(pdf_file)
                # call to create_json_page
                context = {
                    'user_page_url': reverse('ai-team', kwargs={'context': user_page})
                }
                html_message = render_to_string('chat_messages/perm_rag_success.html', context)
                if not create_json:
                    return JsonResponse({'error': 'An error occurred while uploading your page, please upload the file again', 'upload_success': upload_success}) 
                else:
                    return JsonResponse({'message': html_message})
            elif pdf_file == 'no path':
                return JsonResponse({'error': 'No path for PDF file', 'upload_success': upload_success})
            else:
                return JsonResponse({'error': 'File processing failed'}, status=400)
        else:
            return JsonResponse({'error': 'Invalid request method'}, status=405)
    
    def create_json_page(self, user_id, user_email, collection):
        try:
                       
            summary_prompt = _("I need your help because my job is to summarize texts and I have been given a complicated one. Mention the topic of the text, important data such as titles, messages, keywords, focus of the topic, and any URLs mentioned. After extracting this data, make the summary. It is important that you only use the information I provide, not the information you already know about the topic, but the information I give you to make the summary.")
            
            formatted_prompt = self.ai_handler.query_user_collection_with_chat_context(user_email, summary_prompt, collection)
            list_messages = self.ai_handler.update_messages(ia_response=False, prompt=formatted_prompt)
            list_messages = self.ai_handler.load_static_messages(list_messages,'summary')

            summary_response = self.ai_handler.call_ollama_no_rag(list_messages)

            json_generator = jsonPageDescriptionOllama(summary_response)
            json_output = json_generator.generate_json()
            self.json_page.create_page(user_id, json_output)
            return True
        except Exception as e:
            # Mensaje de error que in incluye el error y el user_email bien formateado y el nombre de la función y el summary_response y un salto de linea entre cada campo, el mensaje va en ingles
            email_message = f"Error generating json page for User: {user_email}:\n Error: {e}\nSummary response: {summary_response}\n Json Output: {json_output}\n"
            notice_error("Error generating json page", email_message)
            # print nombre de la función y el error
            print(self.create_json_page.__name__, e)
            return False

class AudioTextManager(View):
    def __init__(self):
        self.audio_text_converter = AudioTextConverter()
    def upload_audio(self, request):
        if request.method == 'POST' and request.FILES['audio']:
            audio_file = request.FILES['audio']
            language = request.POST.get('language') 
            file_name = default_storage.save('users_audio_uploads/' + audio_file.name, ContentFile(audio_file.read()))
            file_path = default_storage.path(file_name)
            print(file_path)
            # Procesar el archivo de audio para obtener el texto transcrito
            transcribed_text = self.audio_text_converter.audio_to_text(file_path, language)
            print(transcribed_text)
            return JsonResponse({'transcribed_text': transcribed_text})
        return JsonResponse({'error': 'Invalid request'}, status=400)
    
    def convert_text_to_audio(self, request):
        if request.method == 'POST':
            data = json.loads(request.body)
            text = data.get('text', '')
            lenguage = data.get('language')
            file_url_generated = self.audio_text_converter.text_to_audio(text, lenguage)
            return JsonResponse({'audio_url': file_url_generated})

        return JsonResponse({'error': 'Invalid request'}, status=400)

# Class to handle the form of Reset Password
class PasswordResetView(PasswordResetView):
    template_name = 'registration/password_reset.html'
    form_class = CustomPasswordResetForm
    success_url = reverse_lazy('password_reset_done')
    email_template_name = 'registration/password_reset_email.html'

    def form_valid(self, form):
        """
        Si el formulario es válido, redirige a la URL de éxito.
        """
        messages.success(self.request, "Se han enviado instrucciones para restablecer tu contraseña a tu correo electrónico, si corresponde a una cuenta existente.")
        return super().form_valid(form)

    def form_invalid(self, form):
        """
        Si el formulario no es válido, vuelve a renderizar la misma página con información del formulario.
        """
        for field, errors in form.errors.items():
            for error in errors:
                messages.error(self.request, f"Error in {field}: {error}")
        return self.render_to_response(self.get_context_data(form=form))

# Handle the form to create an cliente account 
class SignupView(CreateView):
    form_class = SignUpForm
    template_name = 'registration/signup.html'
    success_url = reverse_lazy('login')
    
    def form_invalid(self, form):
        error_details = ''
        fields = {'password1': 'password', 'password2': 'confirm password'}
        for field, errors in form.errors.items():
            for error in errors:
                error_message = f"Error in {fields.get(field, field)}: {error}"
                error_details += error_message + '\n'

        if error_details:
            email_contact =form.cleaned_data.get('email')
            notice_error_forms(f"Signup Form Error: \n{error_details}", email_contact, 'Signup')

        messages.error(self.request, error_details)
        return super().form_invalid(form)
class CustomLoginView(LoginView):
    form_class = CustomLoginForm
    template_name = 'registration/login.html'
    def form_valid(self, form):
        return super().form_valid(form)

    def form_invalid(self, form):
        error_details = ''
        for field, errors in form.errors.items():
            for error in errors:
                error_message = f"Error in field '{field}': {error}"
                error_details += error_message + '\n'
                messages.error(self.request, 'error in both fields: ' + error)

        if error_details:
            email_contact =form.cleaned_data.get('username')
            notice_error_forms(f"Login Form Error: \n{error_details}", email_contact, 'Login')

        
        return super().form_invalid(form)


def custom_logout(request):
    logout(request)
    return redirect('login')
        
class Subscription(View):
    template_name = "subscription.html"
    
    def get(self, request, *args, **kwargs):
        """
        Render the subscription page with all plan details.
        """
        plans = SubscriptionDetail.objects.filter(name__in=["Basic AI Team Subscription", "Premium AI Team Subscription" ])
        
        for plan in plans:
            plan.features_list = json.loads(plan.features_list)
            plan.market_place = json.loads(plan.market_place)
            
        context = {
            "plans": plans,  # Cambiado a "plans" para que sea más claro en el template
            "user": request.user,
            'STRIPE_PUBLIC_KEY': settings.STRIPE_PUBLIC_KEY,
        }
        
        return render(request, self.template_name, context)
    
    def post(self, request, *args, **kwargs):
        # Asegúrate de tener esta función definida
        special_code = request.POST.get('special_code')
        plan_id = request.POST.get('plan_id')
        if special_code:
            # Buscar el plan por el código especial
            try:
                # Obtener el plan
                plan = SubscriptionDetail.objects.get(code=special_code)
                features = json.loads(plan.features_list)  # Decodifica el JSON para obtener la lista
                markets = json.loads(plan.market_place)
                # Construir la respuesta con los detalles del plan
                plan_details = {
                    "name": plan.name,
                    "product_name": plan.product_name,
                    "plan_name": plan.plan_name,
                    "price": plan.price,
                    'plan_id': plan.plan_id,
                    'features': features,
                    'markets': markets,
                    # Añadir otros campos según sea necesario
                }
                return JsonResponse(plan_details)
            except SubscriptionDetail.DoesNotExist:
                # Código no encontrado
                return JsonResponse({"error": "Código no encontrado"}, status=404)
        elif plan_id:
            access_token = generate_access_token()
            if access_token:
                agreement_response = create_subscription_agreement(request, access_token, plan_id)

                if agreement_response.status_code == 201:
                    # Suscripción creada con éxito
                    subscription_data = agreement_response.json()
                    subscription_id = subscription_data.get('id')
                    status = subscription_data.get('status')
                    approval_url = next((link['href'] for link in subscription_data['links'] if link['rel'] == 'approve'), None)
                    if approval_url:
                        # Guardar datos de la suscripción en tu modelo, si es necesario
                        return redirect(approval_url)
                    else:
                        # N0  se pudo obtener la URL de aprobación
                        return JsonResponse({"error": "No se pudo obtener la URL de aprobación"}, status=500)     

def create_subscription_view(request):
    print("create_subscription_view")
    error_message = None

    if request.method == 'POST':
        form = SubscriptionForm(request.POST)
        if form.is_valid():
            print('form valid')
            # Obtener datos del formulario
            product_name = form.cleaned_data['product_name']
            plan_name = form.cleaned_data['plan_name']
            subscription_name = form.cleaned_data['subscription_name']
            price = form.cleaned_data['price']
            subscription_date = form.cleaned_data['date']

            access_token = generate_access_token()

            if access_token:
                print('get the access token')
                product_response = create_product(request, access_token)

                if product_response.status_code == 201:
                    print('product created')
                    product_id = product_response.json().get('id')
                    
                    plan_response = create_plan(request, access_token, product_id, price)

                    if plan_response.status_code == 201:
                        print('plan created')
                        plan_id = plan_response.json().get('id')
                        features = json.dumps(form.cleaned_data['features_list'].split(','))
                        markets = json.dumps(form.cleaned_data['market_place'].split(','))
                        # Guardar los detalles de la suscripción en la base de datos
                        subscription_detail = SubscriptionDetail.objects.create(
                            product_name=product_name,
                            product_id=product_id,
                            plan_name=plan_name,
                            plan_id=plan_id,
                            name=subscription_name,
                            price=price,
                            features_list=features,
                            market_place=markets,
                            subscription_date=subscription_date
                        )
                        try:
                            subscription_detail.save()
                        except Exception as e:
                            print(f"Error saving subscription details: {e}")
                        print('plan saved')
                        generated_code = subscription_detail.code
                        print(generated_code)
                        # Enviar mensaje de éxito
                        try:
                            messages.success(request, f'Subscription details saved successfully. The code of this subscription is: {generated_code}. Remember you can consult this code in the list of subscriptions.')
                        except Exception as e:
                            print(f"Error sending message: {e}")

                        return render(request, 'payment/create_subscription.html', {'form': form})
                    else:
                        error_message = "Failed to create subscription plan. Please try again later."
                else:
                    error_message = "Failed to create product. Please try again later."
            else:
                error_message = "Failed to generate access token. Please check your credentials and try again later."
        else:
            error_message = "Invalid form data. Please check your input."

    else:
        form = SubscriptionForm()

    return render(request, 'payment/create_subscription.html', {'form': form, 'error_message': error_message})


def PaymentSuccessful(request, plan_id):
    # Recuperar el plan de la base de datos
    plan = get_object_or_404(SubscriptionDetail, plan_id=plan_id)

    # Aquí deberías procesar la respuesta de la API de PayPal
    # Por ejemplo, podrías obtener la ID de suscripción de PayPal, el estado de la suscripción, etc.
    # Esto dependerá de cómo estás recibiendo los datos de PayPal en este request
    paypal_subscription_id = request.GET.get("subscription_id", "")
    print("paypal_subscription_id", paypal_subscription_id)
    payment_status = request.GET.get("status", "")
    print("payment_status", payment_status)
    # Suponiendo que tienes un modelo de usuario que almacena estos detalles
    try:
        # Corrección del nombre de la variable
        instance_subscription = SubscriptionDetail.objects.get(plan_id=plan_id)
        print('instance_subscription', instance_subscription)
        user = request.user
        user.is_subscribe = True
        user.order_id = paypal_subscription_id  # ID de suscripción de PayPal
        user.last_transaction_status = payment_status
        user.next_date_pay = datetime.now() + timedelta(days=30)  # Asume un plan mensual
        user.date_subscription = datetime.now()
        user.subscription_detail = instance_subscription
        user.save()
        print("user saved")
    except SubscriptionDetail.DoesNotExist:
        print(f"No subscription detail found with plan_id {plan_id}")
    except Exception as e:
        print(f"Error saving user: {e}")

    return render(request, 'payment/payment_success.html', {'plan': plan})

def PaymentFailed(request, plan_id):
    # Recuperar el plan de la base de datos
    plan = get_object_or_404(SubscriptionDetail, plan_id=plan_id)
    
    return render(request, 'payment/payment_failed.html', {'plan': plan})

def subscription_list_view(request, *args, **kwargs):
    print(request)
    tables = {'clients': User, 'plans': SubscriptionDetail}
    list_all = kwargs.get('list_all')
    table = tables.get(list_all)
    columns = []
    data_rows = []
    if request.method == 'POST' and 'cancel_subscription' in request.POST:
        cancel_order_id = request.POST.get('cancel_subscription')
        cancel_message = cancel_subscription(request, cancel_order_id)

    if table:
        if list_all == 'clients':
            columns = ['email','subscription_detail__plan_name', 'order_id', 'status_subscription', 'next_date_pay', 'date_subscription']
            subscriptions = table.objects.all()
        elif list_all == 'plans':
            columns = ['plan_name', 'code', 'plan_id', 'price', 'name', 'features_list', 'market_place']
            subscriptions = table.objects.all()
            for subscription in subscriptions:
                subscription.features_list = json.loads(subscription.features_list)
                subscription.market_place = json.loads(subscription.market_place)
                features_html = '<ul>' + ''.join([f'<li>{feature}</li>' for feature in subscription.features_list]) + '</ul>'
                marketplace_html = '<ul>' + ''.join([f'<li>{feature}</li>' for feature in subscription.market_place]) + '</ul>'
                row = [getattr(subscription, col, '') for col in columns]

                # Store features_list and marketplace as lists directly
                features_list_index = columns.index('features_list')
                marketplace_index = columns.index('market_place')
                row[features_list_index] = features_html
                row[marketplace_index] = marketplace_html

                data_rows.append(row)
                print(data_rows)

    return render(request, 'payment/list_subscriptions.html', {'data_rows': data_rows, 'columns': columns, 'list_all': list_all})


@csrf_exempt
def error_handler(request):
    print('error handler')
    if request.method == 'POST':
        error_data = request.json
        email = error_data.get('email')
        url = error_data.get('url')
        notice_error_forms(error_data, email, url, side = 'Client Side')
        return JsonResponse({'status': 'error logged'})
    return JsonResponse({'status': 'error'}, status=400)
