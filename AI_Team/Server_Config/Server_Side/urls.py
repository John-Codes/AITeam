from django.urls import path, re_path, include
from django.contrib.auth import views as auth_views
from django.views.generic.base import RedirectView
#from paypal.standard.ipn import views as paypal_views
from . import views
#path('ipn/', paypal_views.ipn, name='paypal-ipn'),

urlpatterns = [
    path('', RedirectView.as_view(url='/ai-team/chat/main/', permanent=False)),
    path('ai-team/chat/<str:context>/', views.ChatUIView.as_view(), name='ai-team'),
    path('ai-team/signup/', views.SignupView.as_view(), name='signup'),
    path('ai-team/login/', views.CustomLoginView.as_view(template_name='registration/login.html'), name='login'),
    path('ai-team/logout/', views.custom_logout, name='logout'),
    path('ai-team/password-reset/', views.PasswordResetView.as_view(template_name='registration/password_reset.html'), name='password_reset'),
    #path('checkout/<int:plan_id>/', views.SubscriptionCheckout, name='subscription-checkout'),
    path('payment-success/<str:plan_id>/', views.PaymentSuccessful, name='payment_success'),
    path('payment-failed/<str:plan_id>/', views.PaymentFailed, name='payment_failed'),
    path('ai-team/subs-page/', views.Subscription.as_view(), name='subscription'),
    path('ai-team/subs-page/create/', views.create_subscription_view, name='create_subscription'),
    path('ai-team/subs-page/list/<str:list_all>', views.subscription_list_view, name='list_subscriptions'),
    path('error-handler/', views.error_handler, name='error_handler'),
    
]