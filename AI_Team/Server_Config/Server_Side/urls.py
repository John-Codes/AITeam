from django.urls import path
from django.contrib.auth import views as auth_views
from django.views.generic.base import RedirectView
from . import views
urlpatterns = [
    path('', RedirectView.as_view(url='ai-team/', permanent=True)),
    path('ai-team/', views.ChatUIView.as_view(), name='ai-team'),
    path('ai-team/signup/', views.SignupView.as_view(), name='signup'),
    path('ai-team/login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('ai-team/logout/', views.custom_logout, name='logout'),
    path('ai-team/password-reset/', views.PasswordResetView.as_view(template_name='registration/password_reset.html'), name='password_reset'),

]