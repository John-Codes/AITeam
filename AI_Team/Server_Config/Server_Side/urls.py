from django.urls import path
from . import views

urlpatterns = [
    path('aiteam/', views.chat_ui, name='chat_ui'),
    path('login/', views.login, name='login'),
]

# this is how login href with html
#<li><a href="{% url 'login' %}">Login</a></li>