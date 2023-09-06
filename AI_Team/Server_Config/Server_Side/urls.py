from django.urls import path
from . import views

urlpatterns = [
    path('aiteam/', views.chat_ui, name='chat_ui'),
    path('login/', views.login, name='login'),
]