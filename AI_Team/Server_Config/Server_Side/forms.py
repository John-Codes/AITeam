from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Client as User

class SignUpForm(UserCreationForm):
    email = forms.EmailField(required=True, help_text="Required.")

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")

class PasswordResetForm(forms.Form):
    username = forms.CharField(label='Username', max_length=150)
    email = forms.EmailField(label='Email')
    newpassword = forms.CharField(label='New Password', widget=forms.PasswordInput)
    confirmpassword = forms.CharField(label='Confirm New Password', widget=forms.PasswordInput)

    def clean(self):
        cleaned_data = super().clean()
        username = cleaned_data.get('username')
        email = cleaned_data.get('email')
        newpassword = cleaned_data.get('newpassword')
        confirmpassword = cleaned_data.get('confirmpassword')

        try:
            user = User.objects.get(username=username, email=email)
        except User.DoesNotExist:
            print("DEBUG: User does not exist with given username and email.")
            raise forms.ValidationError("Username and Email do not match an existing user.")

        if newpassword != confirmpassword:
            print("DEBUG: Passwords entered do not match.")
            raise forms.ValidationError("Passwords do not match.")
        
        return cleaned_data