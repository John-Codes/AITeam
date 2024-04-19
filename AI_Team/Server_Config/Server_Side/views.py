from django.shortcuts import get_object_or_404
from django.conf import settings
import os
import json
from pathlib import Path
from django.http import JsonResponse
from django.http import StreamingHttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy, reverse
from django.views.generic.edit import CreateView 
from django.views import View
from django.contrib.sessions.models import Session
from .forms import * # class to clean an prosces form reset_password
from django.contrib import messages 
from .models import Client as User
from .models import ClienContext, SubscriptionDetail
from django.contrib.auth import logout 
from django.shortcuts import render,redirect 
from AI_Team.Logic.Memory import *
from AI_Team.Logic.response_utils import * # IA message render templates method
from AI_Team.Logic.sender_mails import Contac_us_mail, notice_error_forms
from AI_Team.Logic.Data_Saver import DataSaver
from AI_Team.Logic.ollama.ollama_rag_Module import OllamaRag
from AI_Team.Logic.Cancel_Subscription import cancel_subscription
from AI_Team.Logic.Charge_Context import Charge_Context
from AI_Team.Logic.Chat.pdf_handling import *
from AI_Team.Logic.AIManager.llm_api_Handler_module import ai_Handler

from AI_Team.Logic.AI_Instructions.get_ai_instructions import get_instructions
#from AI_Team.Logic.ollama.ollama_rag_Module import OllamaRag
from .create_paypal import *
from hashids import Hashids
import time
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import PasswordResetView

# Stripe using stripe
import stripe
# PayPal
#from paypal.standard.forms import PayPalPaymentsForm
#from paypal.standard.ipn.models import PayPalIPN
from django.dispatch import receiver
#from paypal.standard.ipn.signals import valid_ipn_received
import uuid
import paypalrestsdk
from django.conf import settings
from AI_Team.Logic.Payments import plans_data
from datetime import datetime, timedelta
#from .models import Current_Plan, PaymentMethod, SubscriptionStatus
from django.utils.translation import gettext as _
stripe.api_key = settings.STRIPE_SECRET_KEY
hashids = Hashids(salt = os.getenv("salt"), min_length=8)
ai = ai_Handler() #so we dont delete the temp rag retriever.

#STRIPE_PUBLIC_KEY': settings.STRIPE_PUBLIC_KEY

# ai-team chat handle events and requests
# SANDBOX MODE
# paypalrestsdk.configure({
#     "mode": "sandbox",  # sandbox or live (production),  # Use 'live' for production
#     "client_id": "AThJhSpO1NlOyyx19jAC5Vb2CStnbrurdgm3hqKzVaVoz85T9lKKoYThf7hKRNYeovC6b_iJOgkXZCMB",
#     "client_secret": "ECk7V4Ntt5PJy4Nosm9g80gMzf2WMvwVptzlmwOzEsxz37FPM_NXa6rCFH8BcR4Mc24odULhHM2eH5Aw"
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
        #self.ollama = OllamaRag()

        #Gets the conversation context
    def get(self, request, *args, **kwargs):
        #chat = Chat_history()
        ai = ai_Handler()
        valid_contexts = ["main", "subscription", "panel-admin"]
        titles = {"main": [_('EFEXZIUM'), _('AI Team Chat')], "subscription": [_('Subscriptions'), _('AI Team Subscriptions')], "panel-admin": [_('Create your own page'), _('AI Team Page Builder')]}
        page_data = DataSaver()
        
        if request.session.get('temp_context_chat', False):
            delete_temp_pdfs(request.session['temp_context_chat'])
            del request.session['temp_context_chat']
        
        self.context_value = kwargs.get('context', None)
        # obtener instrucciones:
        context_data_ai = get_instructions(self.context_value)
        # iniciar el rag dado el path donde esta el contexto o las instrucciones para la IA
        #
        # Si el contexto es uno de los personalizados
        
        if self.context_value not in valid_contexts:
            site_exists = page_data.check_site(check_context=self.context_value)
            if not site_exists:
                return redirect('/chat/main')
            # Extraer el valor real del context
            context_filename = "memory-AI-with-" + self.context_value.split('Uptc%3Fto=')[-1].rstrip('$')
            data_dict = page_data.json_to_dict(context_filename)
            if data_dict:
                context = {
                    'website_data': data_dict,
                    'context_value': self.context_value,
                }
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
                data_dict = page_data.json_to_dict(context_filename)
                
                context = {
                    'title': titles[self.context_value][0],
                    'header': titles[self.context_value][1],
                    'context_value': self.context_value,
                    'valid_contexts': valid_contexts,
                    'site_exists': site_exists
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


    def post(self, request, *args, **kwargs):
        # Preparación de datos de la solicitud
        self.context_value = kwargs.get('context', None)
        template_name = request.POST.get('template_name', None)
        user_message = request.POST.get('message')
        phase = request.POST.get('phase')
        action = request.POST.get('action')
        response_html = ""

        # Archivos temporales
        pdf_file, upload_succes = proccess_context_files(request, self.context_value)
        if pdf_file != 'no path' and upload_succes:
            request.session['temp_context_chat'] = pdf_file
            #ollama.add_pdf_to_new_temp_rag(temp_context_chat)
            ai.create_temp_rag_with_a_pdf(pdf_file)
            response_html += render_html('chat_messages/ia_message.html', upload_succes)
        elif pdf_file == 'no path':
            response_html += render_html('chat_messages/ia_message.html', upload_succes)
        if action == 'cancel_subscription':
            response_html += render_html('chat_messages/cancel.html', '')

        # Manejar plantillas de mensajes
        if template_name:
            template_response = self.handle_template_messages(request, template_name)
            response_html += template_response.get('template_message_div', '')

        # Si hay una respuesta de la IA, procesarla
        if phase == 'ai_response':
            ai_response_data = self.handle_ai_response(request, user_message)
            response_html += ai_response_data.get('ia_message_div', '')

        if not response_html:
            return JsonResponse({"error": "Invalid request"})

        return JsonResponse({'combined_response': response_html})
    
    def handle_template_messages(self, request, template_name):
        response_data = {}
        response_data['template_message_div'] = render_html(f'chat_messages/{template_name}.html', '')
        if template_name == 'contact_us':
            request.session['send_us_email'] = True            
        time.sleep(2)
        return response_data

    def handle_ai_response(self, request, user_message):
        response_data = {}
        product_consult = False
        
        if request.session.get('cancel-subscription', False):
            if str(user_message).lower() == 'yes':

                ai_response = cancel_subscription(request)
            else:
                ai_response = None
            request.session['cancel-subscription'] = False
            del request.session['cancel-subscription']
        else:
            context_ia = self.context_value
            
            if context_ia not in ["main", "subscription", "panel-admin"]:
                context_ia = context_ia.split('Uptc?to=')[-1].rstrip('$')
            # else: 
            #     #Check_Cuestion(user_message)
            #     chat.add_user_message(user_message)
            #     ai_response = ollama.query_ollama(chat.get_messages())

            if context_ia == 'panel-admin':
                reading = DataSaver()#converts to from Json to dic
                # alistamos el prompt para generar el json
                json_read =reading.read_from_json(f'memory-AI-with-{hashids.encode(request.user.id)}')
                # alistamos el prompt para la IA que responde al usuario
                user_message = str(user_message) + f''' This is the data of my page in json remember this to respond:  ''' + str(json_read)
                
           
            if request.session.get('temp_context_chat', False):
                #del request.session['temp_context_chat']
                #ai_response = ollama.query_temp_rag_single_question(user_message)
                ai_response = ai.call_ai_temp_rag(user_message)
            else:
                #ai_response, product_consult = Consulta_IA_PALM(user_message, context_ia)
                ai_response = ai.call_router(user_message,context_ia)
            
        if request.session.get('send_us_email', False):
            # Handle email sending logic
            self.send_email(user_message)
            request.session['send_us_email'] = False
            del request.session['send_us_email']

        if ai_response:
            rendered_product = ''
            if product_consult:
                rendered_product = render_html('chat_messages/message_info_product.html', product_consult)
            response_data['ia_message_div'] = render_html('chat_messages/ia_message.html', ai_response, format=True) + rendered_product

        else:
            error_message = 'The API could not respond.'
            response_data['ia_message_div'] = render_html('chat_messages/ia_message.html',error_message)
        return response_data
      

    def send_email(self, user_message):
        if ('@' and '.') in user_message:
            Contac_us_mail(user_message)  

@csrf_exempt
def stream_chat(request):
    if request.method == 'POST':        
        chat_ollama = OllamaRag()
        data = json.loads(request.body)
        # Acceder al mensaje usando la clave 'content'
        message = data.get('content', None)
        print(message)
        messages = ai.call_router_async(message, 'main')
        
        return StreamingHttpResponse(chat_ollama.stream_query_ollama(messages), content_type='text/event-stream')
    else:
        return JsonResponse({'error': 'Invalid request method'}, status=400)


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
        for field, errors in form.errors.items():
            for error in errors:
                error_message = f"Error in {field}: {error}"
                error_details += error_message + '\n'

        if error_details:
            email_contact =form.cleaned_data.get('email')
            notice_error_forms(f"Signup Form Error: \n{error_details}", email_contact)

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
            notice_error_forms(f"Login Form Error: \n{error_details}", email_contact)

        
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
            print(plan.features_list)
        context = {
            "plans": plans,  # Cambiado a "plans" para que sea más claro en el template
            "user": request.user,
            'STRIPE_PUBLIC_KEY': settings.STRIPE_PUBLIC_KEY,
        } 
        
        return render(request, self.template_name, context)
    
    def post(self, request, *args, **kwargs):
        print('post')
        print(request.POST)
          # Asegúrate de tener esta función definida
        special_code = request.POST.get('special_code')
        plan_id = request.POST.get('plan_id')
        print('especial code detected',special_code)
        if special_code:
            # Buscar el plan por el código especial
            try:
                # Obtener el plan
                plan = SubscriptionDetail.objects.get(code=special_code)
                print('plan',plan)
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
                print('plan_details', plan_details)
                return JsonResponse(plan_details)
            except SubscriptionDetail.DoesNotExist:
                # Código no encontrado
                return JsonResponse({"error": "Código no encontrado"}, status=404)
        elif plan_id:
            access_token = generate_access_token()
            if access_token:
                print('generamos access token')
                # Llama a la función para crear la suscripción
                print(plan_id)
                print(request)
                agreement_response = create_subscription_agreement(request, access_token, plan_id)

                if agreement_response.status_code == 201:
                    # Suscripción creada con éxito
                    print('agreement_response', agreement_response)
                    subscription_data = agreement_response.json()
                    subscription_id = subscription_data.get('id')
                    status = subscription_data.get('status')
                    approval_url = next((link['href'] for link in subscription_data['links'] if link['rel'] == 'approve'), None)
                    print('subscription_id', subscription_id)
                    print('status', status)
                    print('approval_url', approval_url)
                    if approval_url:
                        print('redirecting')
                        print(approval_url)
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
        print(table)
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
        notice_error_forms(error_data)
        return JsonResponse({'status': 'error logged'})
    return JsonResponse({'status': 'error'}, status=400)