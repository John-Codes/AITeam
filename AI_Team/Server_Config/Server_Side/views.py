from django.conf import settings
import os
from pathlib import Path
from django.http import JsonResponse, HttpResponseRedirect # send json objects
from django.contrib.auth.forms import UserCreationForm # handle defaults forms of django
from django.urls import reverse_lazy, reverse
from django.views.generic.edit import CreateView 
from django.views import View
from django.contrib.sessions.models import Session
from .forms import PasswordResetForm, SignUpForm # class to clean an prosces form reset_password
from django.contrib import messages 
from .models import Client as User
from django.contrib.auth import logout 
from django.shortcuts import render,redirect 
from AI_Team.Logic.Memory import *
from AI_Team.Logic.response_utils import * # IA message render templates method
from AI_Team.Logic.sender_mails import Contac_us_mail
from AI_Team.Logic.Data_Saver import DataSaver
from AI_Team.Logic.Cancel_Subscription import cancel_subscription
from AI_Team.Logic.Charge_Context import Charge_Context
from hashids import Hashids
import time
from django.contrib.auth.decorators import login_required
# Stripe using stripe
import stripe
# PayPal
from paypal.standard.forms import PayPalPaymentsForm
from paypal.standard.ipn.models import PayPalIPN
from django.dispatch import receiver
from paypal.standard.ipn.signals import valid_ipn_received
import uuid
from django.conf import settings
from AI_Team.Logic.Payments import plans_data
from datetime import datetime, timedelta
from .models import Current_Plan, PaymentMethod, SubscriptionStatus
stripe.api_key = settings.STRIPE_SECRET_KEY
hashids = Hashids(salt = os.getenv("salt"), min_length=8)
#STRIPE_PUBLIC_KEY': settings.STRIPE_PUBLIC_KEY

# ai-team chat handle events and requests

class ChatUIView(View):
    def __init__(self, *args, **kwargs):
        super(ChatUIView, self).__init__(*args, **kwargs)
        self.context_value = None

    def get(self, request, *args, **kwargs):
        self.context_value = kwargs.get('context', None)
        

        valid_contexts = ["main", "subscription", "panel-admin"]

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

                context = {
                    'my_site_IA': url,
                    'context_value': self.context_value,
                    'valid_contexts': valid_contexts,
                    'site_exists': site_exists
                }
            else:
                context = {
                    'context_value': self.context_value,
                    'valid_contexts': valid_contexts
                
                }
            invoice =request.session.get('invoice', False)
            print(invoice)
            all_registers = PayPalIPN.objects.all()
            print(f"Found {len(all_registers)} PayPalIPN objects")
            if invoice:
                ipn_obj = PayPalIPN.objects.filter(invoice=invoice).first()
                if ipn_obj:
                    request.user.order_id = ipn_obj.subscr_id
                    print(f"Found the order_id object with invoice {request.user.order_id} and payment_status 'Completed'")
                    request.user.save()
                else:
                    print(f"No PayPalIPN object found with invoice {invoice} and payment_status 'Completed'")
                del request.session['invoice']
            return render(request, 'ai-team.html', context)


    def post(self, request, *args, **kwargs):
        # request data preparing
        self.context_value = kwargs.get('context', None)
        template_name = request.POST.get('template_name', None)
        user_message = request.POST.get('message')
        phase = request.POST.get('phase')
        action = request.POST.get('action')
        uploaded_files = request.FILES.getlist('uploaded_files')  # Extracting uploaded files

        # You can process the uploaded_files here if needed
        if uploaded_files:
            self.process_uploaded_files(request, uploaded_files)
        if action == 'cancel_subscription':
            response_data = {}
            request.session['cancel-subscription'] = True
            response_data['template_message_div'] = render_html('chat_messages/cancel.html', '')
            return JsonResponse(response_data)

        if template_name:
            return self.handle_template_messages(request, template_name)

        if phase == 'user_message':
            
            return self.handle_user_message(request, user_message)

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
            
            
        time.sleep(4)
        return JsonResponse(response_data)

    def handle_user_message(self, request, user_message):
        response_data = {}
        response_data['user_message_div'] = render_html('chat_messages/user_message.html', user_message)
        return JsonResponse(response_data)

    def handle_ai_response(self, request, user_message):
        response_data = {}
        
        if request.session.get('cancel-subscription', False):
            if str(user_message).lower() == 'yes':
                ai_response = cancel_subscription(request.user)
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
                # alistamos el prompt para generar el json
                reading =DataSaver()
                json_read =reading.read_from_json(f'memory-AI-with-{hashids.encode(request.user.id)}')
                
                if json_read:
                    prompt = f'this is my dict: {json_read}. now change the dictionary to the next requirements {user_message}'
                else:
                    prompt = user_message
                json_to_IA, tokens_prompt= generate_json(prompt)
                # Precio por token
                TOKEN_PRICE = 0.006

                # Calcula el costo de la nueva solicitud
                current_cost = tokens_prompt * TOKEN_PRICE

                # Suma el costo al total acumulado
                total_cost = request.user.total_tokens + current_cost

                # Actualiza el campo total_tokens y guarda los cambios
                request.user.total_tokens = total_cost
                request.user.save()
                self.create_page(request, json_to_IA)
                # alistamos el prompt para la IA que responde al usuario
                user_message = str(user_message) + 'here is the data you give me, Explain it to me using natural language that isnt hard to understand' + str(json_to_IA)
                # consultamos a la IA, obtenemos la respuesta y la guardamos en el diccionario a enviar
                ai_response, product_consult =  Consulta_IA_PALM(user_message, context_ia)
                response_data['total_cost'] = total_cost
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
            print(product_consult)
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
        for file in uploaded_files:
            try:
                if file.name.endswith('.png'):
                    user = hashids.encode(request.user.id)
                    print(user)
                    charger.save_image_product(user, file)
                else:
                    text = charger.extract_text(file)
                    if text:
                        charger.save_context(request.user.id, text)
            except ValueError as e:
                # Handle errors, such as unsupported file types
                print(e)



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
            messages.success(request, 'Password changed successfully.')
            return redirect('login')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, error)  # Display each error as a message.
            return render(request, self.template_name, {'form': form})

# Handle the form to create an cliente account 
class SignupView(CreateView):
    form_class = SignUpForm
    template_name = 'registration/signup.html'
    success_url = reverse_lazy('login')
    
    def form_valid(self, form):
        user = form.save(commit=False)
        user.email = form.cleaned_data['email']
        user.save()
        messages.success(self.request, 'Account created successfully. You can now log in.')
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, 'There was an error processing your form. Please check the details and try again.')
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
        
        context = {
            "plans": plans_data,  # Cambiado a "plans" para que sea más claro en el template
            "user": request.user,
            'STRIPE_PUBLIC_KEY': settings.STRIPE_PUBLIC_KEY,
        }

        return render(request, self.template_name, context)


"""def payment_success(request):
    return render(request, 'payment/payment_success.html')

def payment_failed(request):
    return render(request, 'payment/payment_failed.html')
"""
def SubscriptionCheckout(request, plan_id):
    print(f"SubscriptionCheckout function called with plan_id {plan_id}")
    # Asegúrate de que plan_id es un índice válido en plans_data
    plan = plans_data[plan_id]

    host = request.get_host()
    invoice_id = uuid.uuid4()
    # Creamos el diccionario para la suscripción
    paypal_dict = {
        "cmd": "_xclick-subscriptions",
        "business": settings.PAYPAL_RECEIVER_EMAIL,
        "a3": plan['amount'] / 100,     # Precio mensual. Convertimos de centavos a dólares
        "p3": 1,                        # Duración de cada unidad (en este caso, meses)
        "t3": "M",                      # Unidad de duración ("M" para Mes)
        "src": "1",                     # Hacer pagos recurrentes
        "sra": "1",                     # Reintentar pago en caso de error
        "no_note": "1",                 # Quitar notas adicionales
        "item_name": plan['name'],
        "invoice": str(invoice_id),
        "notify_url": f"http://{host}{reverse('paypal-ipn')}",
        "return": f"http://{host}{reverse('payment_success', kwargs={'plan_id': plan_id})}",
        "cancel_return": f"http://{host}{reverse('payment_failed', kwargs={'plan_id': plan_id})}",
    }

    paypal_form = PayPalPaymentsForm(initial=paypal_dict, button_type="subscribe")

    context = {
        'plan': plan,
        'paypal': paypal_form
    }
    print(f"Creating a subscription checkout for invoice {invoice_id}")
    request.session['invoice'] = str(invoice_id)
    return render(request, 'payment/subscription_checkout.html', context)

def PaymentSuccessful(request, plan_id):
    print(f"PaymentSuccessful function called with plan_id {plan_id}")
    print('payment successful')
    plan = plans_data[plan_id]
    plan['amount'] = plan['amount'] / 100
    user = request.user 
    invoice = request.session.get('invoice')
    print('invoice id uuid', invoice)
    print('Attempting to retrieve IPN object for invoice id uuid:', invoice)

    # Intenta encontrar el objeto PayPalIPN usando el invoice (uuid)
    try:
        ipn_obj = PayPalIPN.objects.filter(invoice=invoice, payment_status="Completed").first()
        all_registers = PayPalIPN.objects.all()
        print(f"Found {len(all_registers)} PayPalIPN objects")
        if ipn_obj:
            print(f"Found PayPalIPN object with invoice {invoice} and payment_status 'Completed'")
            print(f"Payment date: {ipn_obj.payment_date}, Payment status: {ipn_obj.payment_status}")
        else:
            print(f"No PayPalIPN object found with invoice {invoice} and payment_status 'Completed'")
        paypal_subscription_id = ipn_obj.subscr_id if ipn_obj else 0
    except PayPalIPN.DoesNotExist:
        print(f"PayPalIPN object does not exist for invoice {invoice}")
        paypal_subscription_id = 0

    # Actualizar datos del modelo del usuario
    print(user)
    user.is_subscribe = True
    print('paypal subscription id',paypal_subscription_id)
    user.order_id = paypal_subscription_id
    print('add the id to the user',user.order_id)
    user.last_transaction_status = "Success"
    user.current_plan = Current_Plan.objects.get(current_plan=plan['name'])  
    user.subscription_status = SubscriptionStatus.objects.get(subscription_status="Active")
    user.method_pay = PaymentMethod.objects.get(method_pay="Paypal")
    user.next_date_pay = datetime.now() + timedelta(days=30)  # Asume un plan mensual
    user.date_subscription = datetime.now()
    user.save()

    return render(request, 'payment/payment_success.html', {'plan': plan})


def PaymentFailed(request, plan_id):
    print(f"PaymentFailed function called with plan_id {plan_id}")
    plan = plans_data[plan_id]
    return render(request, 'payment/payment_failed.html', {'plan': plan})