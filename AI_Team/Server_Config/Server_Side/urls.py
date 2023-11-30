from django.urls import path, re_path, include
from django.contrib.auth import views as auth_views
from django.views.generic.base import RedirectView
#from paypal.standard.ipn import views as paypal_views
from . import views
#path('ipn/', paypal_views.ipn, name='paypal-ipn'),

urlpatterns = [
    path('', RedirectView.as_view(url='/chat/main/', permanent=False)),
    path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='registration/password_reset_done.html'), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='registration/password_reset_confirm.html'), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name='registration/password_reset_complete.html'), name='password_reset_complete'),
    path('chat/<str:context>/', views.ChatUIView.as_view(), name='ai-team'),
    path('signup/', views.SignupView.as_view(), name='signup'),
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', views.custom_logout, name='logout'),
    path('password-reset/', views.PasswordResetView.as_view(), name='password_reset'),
    path('payment-success/<str:plan_id>/', views.PaymentSuccessful, name='payment_success'),
    path('payment-failed/<str:plan_id>/', views.PaymentFailed, name='payment_failed'),
    path('subs-page/', views.Subscription.as_view(), name='subscription'),
    path('subs-page/create/', views.create_subscription_view, name='create_subscription'),
    path('subs-page/list/<str:list_all>', views.subscription_list_view, name='list_subscriptions'),
    path('error-handler/', views.error_handler, name='error_handler'),
]