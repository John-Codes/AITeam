from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
urlpatterns = [
    path('', views.home, name='home'),
    path('aiteam/', views.ChatUIView.as_view(), name='chat_ui'),
    path('aiteam/signup/', views.SignupView.as_view(), name='signup'),
    path('aiteam/login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('aiteam/logout/', views.custom_logout, name='logout'),
    path('aiteam/password_reset/', views.PasswordResetView.as_view(template_name='registration/password_reset.html'), name='password_reset'),
]