from django.http import JsonResponse # send json objects
from django.contrib.auth.forms import UserCreationForm # handle defaults forms of django
from django.urls import reverse_lazy
from django.views.generic.edit import CreateView 
from django.views import View
from django.contrib.sessions.models import Session
from .forms import PasswordResetForm, SignUpForm # class to clean an prosces form reset_password
from django.contrib import messages 
from django.contrib.auth.models import User
from django.contrib.auth import logout 
from django.shortcuts import render,redirect 
from AI_Team.Logic.LLMs import Call, Check_Cuestion # IA methods
from AI_Team.Logic.Memory import consulta_IA_openai
from AI_Team.Logic.response_utils import render_html # IA message render templates method
from AI_Team.Logic.sender_mails import Contac_us_mail
import time

# redirect the pattern url to chatui
"""def home(request):
    if request.method =='GET':
        return redirect('ai-team')"""

# ai-team handle events and requests

class ChatUIView(View):
    def get(self, request, *args, **kwargs):
        # Render the chat UI template for non-POST requests.
        return render(request, 'ai-team.html')

    def post(self, request, *args, **kwargs):
        template_name = request.POST.get('template_name', None)
        user_message = request.POST.get('message')
        phase = request.POST.get('phase')

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
        time.sleep(5)
        return JsonResponse(response_data)

    def handle_user_message(self, request, user_message):
        response_data = {}
        response_data['user_message_div'] = render_html('chat_messages/user_message.html', user_message)
        return JsonResponse(response_data)

    def handle_ai_response(self, request, user_message):
        response_data = {}
        if request.session.get('send_us_email', False):
            # Handle email sending logic
            self.send_email(user_message)
            request.session['send_us_email'] = False
            del request.session['send_us_email']
            return JsonResponse(response_data)
        
        # AI consultation logic
        ai_response = consulta_IA_openai(user_message)
        if ai_response:
            response_data['ia_message_div'] = render_html('chat_messages/ia_message.html', ai_response, format=True)
        else:
            response_data['error'] = 'The API could not respond.'
        
        return JsonResponse(response_data)

    def send_email(self, user_message):
        if ('@' and '.') in user_message:
            Contac_us_mail(user_message)


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
