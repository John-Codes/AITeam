from django.shortcuts import get_object_or_404
from django.conf import settings
import os
from pathlib import Path
from django.http import JsonResponse, HttpResponseRedirect # send json objects
from django.contrib.auth.forms import UserCreationForm # handle defaults forms of django
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
from AI_Team.Logic.Cancel_Subscription import cancel_subscription
from AI_Team.Logic.Charge_Context import Charge_Context
from .create_paypal import *
from hashids import Hashids
import time
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
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
#STRIPE_PUBLIC_KEY': settings.STRIPE_PUBLIC_KEY

# ai-team chat handle events and requests
paypalrestsdk.configure({
    "mode": "sandbox",  # Use 'live' for production
    "client_id": "AThJhSpO1NlOyyx19jAC5Vb2CStnbrurdgm3hqKzVaVoz85T9lKKoYThf7hKRNYeovC6b_iJOgkXZCMB",
    "client_secret": "ECk7V4Ntt5PJy4Nosm9g80gMzf2WMvwVptzlmwOzEsxz37FPM_NXa6rCFH8BcR4Mc24odULhHM2eH5Aw"
})

class ChatUIView(View):
    def __init__(self, *args, **kwargs):
        super(ChatUIView, self).__init__(*args, **kwargs)
        self.context_value = None

    def get(self, request, *args, **kwargs):
        self.context_value = kwargs.get('context', None)
        valid_contexts = ["main", "subscription", "panel-admin"]
        titles = {"main": [_('EFEXZIUM'), _('AI Team Chat')], "subscription": [_('Subscriptions'), _('AI Team Subscriptions')], "panel-admin": [_('Create your own page'), _('AI Team Page Builder')]}
        # Si el contexto es uno de los personalizados
        if self.context_value not in valid_contexts:
            site_exists = self.check_my_own_site_exists(check_context=self.context_value)
            if not site_exists:
                return redirect('/ai-team/chat/main')
            # Extraer el valor real del contexto
            extract = DataSaver()
            context_filename = "memory-AI-with-" + self.context_value.split('Uptc%3Fto=')[-1].rstrip('$')
            data_dict = extract.json_to_dict(context_filename)
            if data_dict:
                context = {
                    'website_data': data_dict,
                    'context_value': self.context_value,
                }
                return render(request, 'ai-team-customize.html', context)

        # Si el contexto es uno de los predeterminados
        else:
            user_id = request.user.id
            site_exists = self.check_my_own_site_exists(user_id)

            # Si el usuario está autenticado, obtenemos la URL del sitio del usuario.
            if request.user.is_authenticated:
                hashed_id = hashids.encode(user_id)
                user_page = f'Uptc%3Fto={hashed_id}$'
                url = reverse('ai-team', kwargs={'context': user_page})
                extract = DataSaver()
                context_filename = "memory-AI-with-" + hashed_id
                data_dict = extract.json_to_dict(context_filename)
                context = {
                    'title': titles[self.context_value][0],
                    'header': titles[self.context_value][1],
                    'context_value': self.context_value,
                    'valid_contexts': valid_contexts,
                    'site_exists': site_exists
                }
                if site_exists:
                    context['my_site_IA']: url
                    context['my_site_title']: data_dict['header']
            else:
                context = {
                    'title': titles[self.context_value][0],
                    'header': titles[self.context_value][1],
                    'context_value': self.context_value,
                    'valid_contexts': valid_contexts
                
                }

            return render(request, 'ai-team.html', context)


    def post(self, request, *args, **kwargs):
        # request data preparing
        self.context_value = kwargs.get('context', None)
        template_name = request.POST.get('template_name', None)
        user_message = request.POST.get('message')
        phase = request.POST.get('phase')
        action = request.POST.get('action')
        uploaded_files = request.FILES.getlist('uploaded_files')  # Extracting uploaded files
        upload_details = None

        # You can process the uploaded_files here if needed
        if uploaded_files:
            #print(f"Uploaded files: {uploaded_files}")
            upload_details = self.process_uploaded_files(request, uploaded_files)
            
        if action == 'cancel_subscription':
            print('action')
            response_data = {}
            request.session['cancel-subscription'] = True
            response_data['template_message_div'] = render_html('chat_messages/cancel.html', '')
            return JsonResponse(response_data)

        if template_name:
            return self.handle_template_messages(request, template_name)

        if phase == 'user_message':
            return self.handle_user_message(request, user_message, upload_details)

        if phase == 'ai_response':
            
            return self.handle_ai_response(request, user_message)

        return JsonResponse({"error": "Invalid request"})


    def handle_template_messages(self, request, template_name):
        response_data = {}
        if template_name == 'faqs_messages':
            response_data['template_message_div'] = render_html('chat_messages/faqs_messages.html', '')
        elif template_name == 'contact_us':
            request.session['send_us_email'] = True
            response_data['template_message_div'] = render_html('chat_messages/contact_us_message.html', '')
        elif template_name == 'about_us':
            response_data['template_message_div'] = render_html('chat_messages/about_us_message.html', '')
        elif template_name == 'create-page':
            request.session['create-web-page'] = True
            response_data['template_message_div'] = render_html('chat_messages/confirm-data-to create-page.html', '')
            
            
        time.sleep(3)
        return JsonResponse(response_data)

    def handle_user_message(self, request, user_message = '', uploaded_files=None):
        response_data = {}
        
        # Inicializa la clave 'user_message_div' con el HTML del mensaje del usuario
        if user_message:
            response_data['user_message_div'] = render_html('chat_messages/user_message.html', message= user_message)
        else:
            response_data['user_message_div'] = ''

        # Si hay archivos cargados, procesa cada uno y concatena el contenido al HTML del mensaje del usuario
        if uploaded_files:
            for file_detail in uploaded_files:
                if file_detail['type'] == 'image':
                    # Renderiza la imagen y concatena al HTML del mensaje del usuario
                    image_html = render_html('chat_messages/image_message.html', file_detail)
                    response_data['user_message_div'] += image_html
                elif file_detail['type'] == 'text':
                    if file_detail['keywords']:
                        print('keywords found', file_detail['keywords'])
                        request.session['create-json-page'] = True
                    request.session['create-json-page'] = True
                    # Renderiza el texto y concatena al HTML del mensaje del usuario
                    text_html = render_html('chat_messages/text_message.html', file_detail)
                    response_data['user_message_div'] += text_html
        return JsonResponse(response_data)

    def handle_ai_response(self, request, user_message):
        response_data = {}
        product_consult = False
        
        if request.session.get('cancel-subscription', False):
            print('cancel subscription')
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
            else: 
                Check_Cuestion(user_message)
            if context_ia == 'panel-admin':
                reading = DataSaver()
                # alistamos el prompt para generar el json
                json_read =reading.read_from_json(f'memory-AI-with-{hashids.encode(request.user.id)}')

                # verificamos que existe el json para pasarle el prompt a la IA 
                #prompt = f'this is my dict: {json_read}. now change the dictionary to the next requirements {user_message}' if json_read else user_message

                # comprobomos si el cliente ya tiene un contexto y si la variable de sesion create-json-page es True
                generate = request.session.get('create-json-page', False)
                if generate:
                    try:
                        client_id = request.user.id
                        client_context = ClienContext.objects.get(client=client_id)
                    except:
                        
                        client_context = False
                    if client_context.context:
                        
                        request.session['create-json-page'] = False
                        json_read, tokens_prompt= generate_json(client_context.context)
                        self.create_page(request, json_read)
                        
                # alistamos el prompt para la IA que responde al usuario
                user_message = str(user_message) + f'''here is the data you give me, 
                please explain it to me using natural language and short as possible 
                that isnt hard to understand''' + str(json_read)
                # consultamos a la IA, obtenemos la respuesta y la guardamos en el diccionario a enviar
                print('llamamos a la IA en panel admin')
                ai_response, product_consult =  Consulta_IA_PALM(user_message, context_ia)
                response_data['total_cost'] = 0
            # AI consultation logic
            else:
                ai_response, product_consult = Consulta_IA_PALM(user_message, context_ia)
                
        if request.session.get('send_us_email', False):
            # Handle email sending logic
            self.send_email(user_message)
            request.session['send_us_email'] = False
            del request.session['send_us_email']

        elif ai_response:
            rendered_product = ''
            if product_consult:
                rendered_product = render_html('chat_messages/message_info_product.html', product_consult)
            response_data['ia_message_div'] = render_html('chat_messages/ia_message.html', ai_response, format=True) + rendered_product

        else:
            response_data['error'] = 'The API could not respond.'
        
        return JsonResponse(response_data)
      

    def send_email(self, user_message):
        if ('@' and '.') in user_message:
            Contac_us_mail(user_message)

    def create_page(self,requests, user_json_page):
        user_name_page = hashids.encode(requests.user.id)
        saver = DataSaver()
        data_dict =saver.format_str_to_dict(user_json_page)
        saver.save_to_json(data_dict, f"memory-AI-with-{user_name_page}")
    
    def check_my_own_site_exists(self, user_id=None, check_context=None):
        """Checks if the user has a personal site saved or if a given context is valid."""
        if user_id:
            # If user_id is provided, generate the filename using hashid
            filename = f"memory-AI-with-{hashids.encode(user_id)}"
            
        elif check_context and check_context.startswith('Uptc%3Fto='):
            # If check_context is provided, generate the filename using context
            filename = f"memory-AI-with-{check_context.split('Uptc%3Fto=')[1].rstrip('$')}"
        else:
            return False

        saver = DataSaver()
        exists = saver.file_exists(filename)
        
        # Print whether the file exists or not
        return exists
    
    def process_uploaded_files(self, request, uploaded_files):
        charger = Charge_Context()
        upload_details = []  # Lista para almacenar detalles de los archivos procesados

        for file in uploaded_files:
            file_detail = {}  # Diccionario para almacenar los detalles de un archivo
            try:
                print('file', file)
                print(file.name)
                if file.name.endswith('.png'):
                    user = hashids.encode(request.user.id)
                    file_detail = charger.save_image_product(user, file)
                    file_detail['type'] = 'image'                    
                else:
                    print('no es imagen')
                    file_detail = charger.extract_text(request.user.id, file)
                    file_detail['type'] = 'text'
                
                upload_details.append(file_detail)
            except Exception as e:
                file_detail['error_server'] = str(e)
                image_seve_fail_email(file_detail, request.user)
                print(f"Error processing file {file.name}: {e}")

        return upload_details

# Class to handle the form of Reset Password
class PasswordResetView(View):
    template_name = 'registration/password_reset.html'
    form_class = PasswordResetForm

    def get(self, request, *args, **kwargs):
        form = self.form_class()
        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            newpassword = form.cleaned_data['newpassword']
            user = User.objects.get(username=username)
            user.set_password(newpassword)
            user.save()
            messages.success(request, _('Password changed successfully.'))
            return redirect('login')
        else:
            error_details = ''
            for field, errors in form.errors.items():
                for error in errors:
                    error_message = f"Error in field '{field}': {error}"
                    messages.error(request, error_message)
                    error_details += error_message + '\n'

            if error_details:
                notice_error_forms(f"Password Reset Error: \n{error_details}")
            return render(request, self.template_name, {'form': form})

# Handle the form to create an cliente account 
class SignupView(CreateView):
    form_class = SignUpForm
    template_name = 'registration/signup.html'
    success_url = reverse_lazy('login')
    
    def form_invalid(self, form):
        error_details = ''
        for field, errors in form.errors.items():
            for error in errors:
                error_message = f"Error in field '{field}': {error}"
                error_details += error_message + '\n'

        if error_details:
            notice_error_forms(f"Signup Form Error: \n{error_details}")

        messages.error(self.request, _('There was an error processing your form. Please check the details and try again.'))
        return super().form_invalid(form)

class CustomLoginView(LoginView):
    def form_valid(self, form):
        return super().form_valid(form)

    def form_invalid(self, form):
        error_details = ''
        for field, errors in form.errors.items():
            for error in errors:
                error_message = f"Error in field '{field}': {error}"
                error_details += error_message + '\n'

        if error_details:
            notice_error_forms(f"Login Form Error: \n{error_details}")

        messages.error(self.request, _('There was an error processing your form. Please check the details and try again.'))
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
        plans = SubscriptionDetail.objects.filter(name__in=["Entry Suscripccion", "Premium Suscripcion", ])
        for plan in plans:
            plan.features_list = json.loads(plan.features_list)
            plan.market_place = json.loads(plan.market_place)
        context = {
            "plans": plans,  # Cambiado a "plans" para que sea más claro en el template
            "user": request.user,
            'STRIPE_PUBLIC_KEY': settings.STRIPE_PUBLIC_KEY,
        } 
        print(context)
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
    tablas = {'clients': User, 'plans': SubscriptionDetail}
    list_all = kwargs.get('list_all')
    table = tablas.get(list_all)

    columns = []
    data_rows = []
    if request.method == 'POST' and 'cancel_subscription' in request.POST:
        cancel_order_id = request.POST.get('cancel_subscription')
        cancel_message = cancel_subscription(request, cancel_order_id)

    if table:
        if list_all == 'clients':
            columns = ['username','subscription_detail__plan_name', 'order_id', 'status_subscription', 'next_date_pay', 'date_subscription']
            subscriptions = table.objects.all()
        elif list_all == 'plans':
            columns = ['plan_name', 'code', 'plan_id', 'price', 'name', 'features_list', 'market_place']
            subscriptions = table.objects.all()
        
        for subscription in subscriptions:
            row = [getattr(subscription, col, '') for col in columns]
            data_rows.append(row)

    return render(request, 'payment/list_subscriptions.html', {'data_rows': data_rows, 'columns': columns, 'list_all': list_all})


@csrf_exempt
def error_handler(request):
    print('error handler')
    if request.method == 'POST':
        error_data = request.json
        notice_error_forms(error_data)
        return JsonResponse({'status': 'error logged'})
    return JsonResponse({'status': 'error'}, status=400)