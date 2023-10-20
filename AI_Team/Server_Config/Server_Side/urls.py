from django.urls import path, re_path, include
from django.contrib.auth import views as auth_views
from django.views.generic.base import RedirectView
from . import views

urlpatterns = [
    path('', RedirectView.as_view(url='/ai-team/chat/main/', permanent=False)),
    path('ai-team/chat/<str:context>/', views.ChatUIView.as_view(), name='ai-team'),
    path('ai-team/signup/', views.SignupView.as_view(), name='signup'),
    path('ai-team/login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('ai-team/logout/', views.custom_logout, name='logout'),
    path('ai-team/password-reset/', views.PasswordResetView.as_view(template_name='registration/password_reset.html'), name='password_reset'),
    path('checkout/<int:plan_id>/', views.SubscriptionCheckout, name='subscription-checkout'),
    path('payment-success/<int:plan_id>/', views.PaymentSuccessful, name='payment_success'),
    path('payment-failed/<int:plan_id>/', views.PaymentFailed, name='payment_failed'),
    path('ai-team/subs-page/', views.Subscription.as_view(), name='subscription'),
    path('', include('paypal.standard.ipn.urls'))
]