from django.contrib.auth.forms import AuthenticationForm
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.forms import PasswordResetForm
from .models import Client as User
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

class SignUpForm(UserCreationForm):
    email = forms.EmailField(required=True, help_text="Required.")

    class Meta:
        model = User
        fields = ("email", "password1", "password2")

    def save(self, commit=True):
        user = super().save(commit=False)
        user.username = self.cleaned_data['email']  # Opcional: asigna el correo electrónico al nombre de usuario
        if commit:
            user.save()
        return user

class CustomPasswordResetForm(PasswordResetForm):
    def clean_email(self):
        email = self.cleaned_data['email']
        UserModel = get_user_model()
        
        # Verificar si existe un usuario con ese correo electrónico
        if not UserModel.objects.filter(email=email).exists():
            raise forms.ValidationError(_("There are no registered users with this email."))
        
        return email
    
class CustomLoginForm(AuthenticationForm):
    username = forms.EmailField(
        label=_("Email"),
        max_length=255,
        widget=forms.TextInput(attrs={'autofocus': True, 'type': 'email'})
    )
    password = forms.CharField(
        label=_("Password"),
        strip=False,
        widget=forms.PasswordInput
    )

    def clean_username(self):
        username = self.cleaned_data.get('username')
        return username.lower()

    def confirm_login_allowed(self, user):
        if not user.is_active:
            raise forms.ValidationError(
                _("This account is inactive."),
                code='inactive',
            )

class SubscriptionForm(forms.Form):
    plan_name = forms.CharField(max_length=100, required=True)
    product_name = forms.CharField(max_length=100, required=True)
    subscription_name = forms.CharField(max_length=100, required=True)
    date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}), required=True)
    price = forms.DecimalField(max_digits=10, decimal_places=2, required=True)
    features_list = forms.CharField(widget=forms.Textarea, required=False)  # Campo de texto para características
    market_place = forms.CharField(widget=forms.Textarea, required=False)  # Campo de texto para mercados