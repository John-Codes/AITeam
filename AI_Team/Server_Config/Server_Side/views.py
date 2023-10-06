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
from hashids import Hashids
import time
from django.contrib.auth.decorators import login_required
# Stripe using stripe
import stripe
# PayPal
from paypal.standard.forms import PayPalPaymentsForm
from paypal.standard.ipn.models import PayPalIPN
import uuid
from django.conf import settings
from AI_Team.Logic.Payments import plans_data
from datetime import datetime, timedelta
from .models import Current_Plan, PaymentMethod, SubscriptionStatus
stripe.api_key = settings.STRIPE_SECRET_KEY
hashids = Hashids(salt = 'ia is the future salt', min_length=8)
#STRIPE_PUBLIC_KEY': settings.STRIPE_PUBLIC_KEY

# ai-team chat handle events and requests

class ChatUIView(View):
    def __init__(self, *args, **kwargs):
        super(ChatUIView, self).__init__(*args, **kwargs)
        self.context_value = None

    def get(self, request, *args, **kwargs):
        self.context_value = kwargs.get('context', None)
        print('GET - context_value:', self.context_value)  # print for debugging
        # We call the validation method
        response = self.validate_context(request)
        if response:  # If validate_context returns something, it is a redirect that we must return
            return response

        # Check if it's a user-specific context and not one of the predefined contexts
        if self.context_value not in ["main", "subscription", "panel-admin"]:
            saver = DataSaver()
            data_dict = saver.json_to_dict(self.context_value)
            # If the data_dict exists, render the customized template
            if data_dict:
                context = {
                    'website_data': data_dict,
                    'context_value': self.context_value,
                }
                return render(request, 'ai-team-customize.html', context)
        else:
            if request.user.is_authenticated:
                user_id = request.user.id
                hashed_id = hashids.encode(user_id)
                user_page = f'Uptc?to={hashed_id}$'
                url = reverse('ai-team', kwargs={'context': user_page})
                context = {
                    'my_site_IA': url,
                    'context_value': self.context_value,
                    'valid_contexts': {"main", "panel-admin", "subscription"},
                    'sites_exists': self.check_my_own_site_exists(self.context_value)
                }
                return render(request, 'ai-team.html', context) 
            else:
                return render(request, 'ai-team.html')

    def post(self, request, *args, **kwargs):
        #request data preparing
        self.context_value = kwargs.get('context', None)
        template_name = request.POST.get('template_name', None)
        user_message = request.POST.get('message')
        phase = request.POST.get('phase')
        action = request.POST.get('action')

        if action == 'cancel_subscription':
            response_data = {}
            print('boton activado')
            request.session['cancel-subscription'] = True
            response_data['template_message_div'] = render_html('chat_messages/cancel.html', '')
            return JsonResponse(response_data)

        if template_name:
            print('template name:', template_name)
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
            request.session['send_us_email'] = False
            del request.session['send_us_email']
        else:
            # AI consultation logic
            ai_response = Consulta_IA_PALM(user_message, self.context_value)

        if request.session.get('send_us_email', False):
            # Handle email sending logic
            self.send_email(user_message)
            request.session['send_us_email'] = False
            del request.session['send_us_email']

        elif request.session.get('create-web-page', False):
            create_page_response = self.create_page(user_message, ai_response)
            response_data['ia_message_div'] = render_html('chat_messages/ia_message.html', create_page_response)
            request.session['create-web-page'] = False
            del request.session['create-web-page']

        elif ai_response:
            response_data['ia_message_div'] = render_html('chat_messages/ia_message.html', ai_response, format=True)

        else:
            response_data['error'] = 'The API could not respond.'
        
        return JsonResponse(response_data)
      

    def send_email(self, user_message):
        if ('@' and '.') in user_message:
            Contac_us_mail(user_message)

    def create_page(self, user_message, ai_response):
        if "yes" in user_message.lower():
            response = extract_ai_dictionary(user_message, self.context_value)
            return response
        return {"message": "User did not confirm"}
    
    def validate_context(self, request):
        """Valida el contexto y redirige si es necesario."""
        valid_contexts = ["main", "subscription", "panel-admin"]
        
        # Si el usuario no está autenticado y trata de acceder a un contexto que no sea "main",
        # o si el contexto no es válido, redirige al usuario a "main"
        if (not request.user.is_authenticated and self.context_value != "main") or \
        (self.context_value not in valid_contexts):
            return redirect('/ai-team/chat/main')
        
        # Check for user-specific context
        elif self.context_value.startswith('Uptc?to='):
            try:
                hashed_id_with_dollar = self.context_value.split('Uptc?to=')[1]
                hashed_id = hashed_id_with_dollar.rstrip('$')  # Remover el signo $ del final si está presente
                user_id = hashids.decode(hashed_id)
            except:
                pass
            
            if not user_id or not User.objects.filter(id=user_id).exists():
                return redirect('/ai-team/chat/main')
                
        return None

    
    def check_my_own_site_exists(self, context):
        current_dir = Path(__file__).parent
        file_path = current_dir / "memory_text" / f"memory-AI-with-{context}.json"
        return os.path.exists(file_path)



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


def payment_success(request):
    return render(request, 'payment/payment_success.html')

def payment_failed(request):
    return render(request, 'payment/payment_failed.html')

def SubscriptionCheckout(request, plan_id):
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
    request.session['invoice'] = str(invoice_id)
    return render(request, 'payment/subscription_checkout.html', context)

def PaymentSuccessful(request, plan_id):
    plan = plans_data[plan_id]
    plan['amount'] = plan['amount'] / 100
    user = request.user 
    invoice = request.session.get('invoice')
    print('invoice id uuid', invoice)

    # Intenta encontrar el objeto PayPalIPN usando el invoice (uuid)
    try:
        ipn_obj = PayPalIPN.objects.filter(invoice=invoice, payment_status="Completed").first()
        paypal_subscription_id = ipn_obj.subscr_id if ipn_obj else None
    except PayPalIPN.DoesNotExist:
        paypal_subscription_id = None

    # Actualizar datos del modelo del usuario
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
    plan = plans_data[plan_id]
    return render(request, 'payment/payment_failed.html', {'plan': plan})