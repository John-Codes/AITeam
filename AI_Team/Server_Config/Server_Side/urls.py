from django.urls import path, re_path, include
from django.contrib.auth import views as auth_views
from django.views.generic.base import RedirectView
from django.contrib.sitemaps.views import sitemap
from .sitemaps import StaticViewSitemap
from . import views
from .views import handle_template_messages, handle_cancel_subscription, handle_interaction_user_messages, send_contact_email, upload_audio
from .views import Conversation
sitemaps = {
    'mymodel': StaticViewSitemap,
}
#from paypal.standard.ipn import views as paypal_views
conversation_instance = Conversation()
#path('ipn/', paypal_views.ipn, name='paypal-ipn'),

urlpatterns = [
    path('', RedirectView.as_view(url='/chat/main/', permanent=False)),
    path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='registration/password_reset_done.html'), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='registration/password_reset_confirm.html'), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name='registration/password_reset_complete.html'), name='password_reset_complete'),
    path('chat/<str:context>/', views.ChatUIView.as_view(), name='ai-team'),
    path('stream-chat/', conversation_instance.stream_chat, name='stream_chat'),
    path('main-query-temp-rag/', conversation_instance.main_query_temp_rag_if_it_exist, name='main_query_temp_rag'),
    path('main-query-perm-rag/', conversation_instance.main_query_perm_rag_if_it_exist, name='main_query_perm_rag'),
    path('static-messages/', handle_template_messages, name = 'static_messages'),
    path('send-contact-email/', send_contact_email, name = 'send_contact_email'),
    path('interaction-user-messages/', handle_interaction_user_messages, name = 'interaction_user_messages'),
    path('cancel-subscription/', handle_cancel_subscription, name = 'cancel_subscription'),
    path('upload_audio/', upload_audio, name='upload_audio'),
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
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap')
]