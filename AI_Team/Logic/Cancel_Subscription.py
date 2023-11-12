from django.contrib import messages
from paypal.standard.ipn.models import PayPalIPN
from Server_Config.Server_Side.models import SubscriptionStatus
from django.conf import settings
import requests

client_id =  "AQMIrYAiPvK-xGhOlI3k05qwaekR81F85JIor0S0iMMgyMvXwDbB1lGwAHIfYw5abnmQDJIAr70m-QKC",
client_secret =  'ENzXZs1hIYTolXArxx4q0lLMsb4rg4S9DmlwEJbyepMpVR-uRhiHwiJphoYt1pO_wMuMXBdK-9zd8xoo'

def cancel_subscription(subscription_id):
    subscription_id = 'I-GDEF492RUYJC'
    global client_id, client_secret 
    # Obtener el token de acceso
    url = "https://api.sandbox.paypal.com/v1/oauth2/token"
    headers = {
        "Accept": "application/json",
        "Accept-Language": "en_US"
    }
    data = {
        "grant_type": "client_credentials"
    }
    auth = ("AQMIrYAiPvK-xGhOlI3k05qwaekR81F85JIor0S0iMMgyMvXwDbB1lGwAHIfYw5abnmQDJIAr70m-QKC", "ENzXZs1hIYTolXArxx4q0lLMsb4rg4S9DmlwEJbyepMpVR-uRhiHwiJphoYt1pO_wMuMXBdK-9zd8xoo")  # Reemplaza "client_id" y "client_secret" con tus propias credenciales de PayPal

    response = requests.post(url, headers=headers, data=data, auth=auth)
    if response.status_code == 200:
        response_data = response.json()
        access_token = response_data["access_token"]
        print(access_token)
        
        # Comprobar si la suscripción existe
        url = f"https://www.sandbox.paypal.com/billing/subscriptions/{subscription_id}"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {access_token}",
        }
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            print("Detalles de la suscripción:", response)
        else:
            print(f"Hubo un error al obtener los detalles de la suscripción: {response.content}")
            return "Error al obtener los detalles de la suscripción:"
        
        # Cancelar la suscripción
        url = f'https://api.sandbox.paypal.com/v1/billing/subscriptions/{subscription_id}/cancel'
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {access_token}'
        }
        body = {
            "reason": "Cancelar la suscripción"  # Puedes personalizar esto con tu propio motivo
        }
        data = '{ "reason": "Not satisfied with the service" }'
        response = requests.post(url, headers=headers, json=body)
        print(response.url)
        if response.status_code == 204:
            print("La suscripción se ha cancelado exitosamente.")
            return "La suscripción se ha cancelado exitosamente."
        else:
            print("Error al cancelar la suscripción:", response.status_code, response.text)
            return "Error al cancelar la suscripción:"
    else:
        print("Error al obtener el token de acceso:", response.status_code, response.text)
        return "Error al obtener el token de acceso:"