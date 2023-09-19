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
from .models import UserQuestion
import time

# redirect the pattern url to chatui
def home(request):
    if request.method =='GET':
        return redirect('chat_ui')

# chat_ui handle events and requests

class ChatUIView(View):
    def get(self, request, *args, **kwargs):
        # Render the chat UI template for non-POST requests.
        return render(request, 'chat_ui.html')

    def post(self, request, *args, **kwargs):
        # Initializing the response_data dictionary.
        response_data = {}

        user_message = request.POST.get('message')
        phase = request.POST.get('phase')
        template_name = request.POST.get('template_name', None)

        # handle default messages, faqs message, contact us message and about us message
        if template_name:
            if template_name == 'faqs_messages':
                response_data['template_message_div'] = render_html('chat_messages/faqs_messages.html', '')
            elif template_name == 'contact_us':
                response_data['template_message_div'] = render_html('chat_messages/contact_us_message.html', '')
            elif template_name == 'about_us':
                response_data['template_message_div'] = render_html('chat_messages/about_us_message.html', '')
            time.sleep(5)
            return JsonResponse(response_data)
        
        # Handle the user's message.
        if phase == 'user_message':
            response_data['user_message_div'] = render_html('chat_messages/user_message.html', user_message)
            return JsonResponse(response_data)

        # Handle the AI's response.
        elif phase == 'ai_response':
            try:
                if '@myemail' in user_message and user_message[0] == '@':
                    Contac_us_mail(user_message)
                    
                ai_response = consulta_IA_openai(user_message)

            except Exception as e:
                response_data['error'] = f"Something went wrong: {e}"
                return JsonResponse(response_data, status=500)  # Respond with a 500 status code for internal errors.

            # Ensure the AI returned a response.
            if ai_response:
                response_data['ia_message_div'] = render_html('chat_messages/ia_message.html', ai_response, format=True)
                Check_Cuestion(user_message)
            else:
                response_data['error'] = 'The API could not respond.'
                return JsonResponse(response_data, status=400)  # Respond with a 400 status code for bad requests.
            
            return JsonResponse(response_data)


class FAQView(View):
    template_name = 'faqs.html'

    def get(self, request, *args, **kwargs):
        # Puedes añadir lógica aquí si quieres recuperar ciertos datos antes de renderizar la plantilla
        return render(request, self.template_name)

    def post(self, request, *args, **kwargs):
        # Recuperar la pregunta del usuario desde el formulario
        user_question = request.POST.get('userMessage')

        if user_question:
            # Guardar la pregunta en la base de datos
            UserQuestion.objects.create(question_text=user_question)

        # Redirigir al usuario de vuelta a la página de FAQs después de enviar su pregunta
        return redirect('faqs')  # Asegúrate de que 'faqs' es el nombre correcto de la URL para esta vista en tu urls.py

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
