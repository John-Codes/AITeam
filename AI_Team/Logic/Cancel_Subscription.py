import paypalrestsdk
from django.contrib import messages
from paypal.standard.ipn.models import PayPalIPN
from paypalrestsdk import BillingAgreement
from Server_Config.Server_Side.models import SubscriptionStatus
from django.conf import settings
import requests
paypalrestsdk.configure({
    "mode": "sandbox",  # Puedes cambiar esto a "live" cuando vayas a producción
    "client_id": settings.PCI,
    "client_secret": settings.PCS
    })

"""def cancel_subscription(user):
    print("Cancelling subscription for user:", user.id)
    paypalrestsdk.configure({
    "mode": "sandbox",  # Puedes cambiar esto a "live" cuando vayas a producción
    "client_id": settings.PCI,
    "client_secret": settings.PCS
    })
    print("Initiating cancel_subscription for user:", user.id)  # Assuming user has an id attribute
    
    # Obtener el ID de la suscripción de PayPal
    paypal_subscription_id = user.order_id
    print("User's PayPal subscription ID:", paypal_subscription_id)

    if not paypal_subscription_id:
        print("Error: Couldn't find subscription details for user:", user.id)
        return "Couldn't find your subscription details."

    try:
        print("Attempting to fetch the Billing Agreement for:", paypal_subscription_id)
        agreement = BillingAgreement.find(paypal_subscription_id)
    except Exception as e:
        print("Error al obtener el acuerdo:", e)
        return str(e)

    if agreement:
        print("Found Billing Agreement. State:", agreement.state)
        if agreement.state == "Active":
            print("Attempting to cancel the active subscription...")
            if agreement.cancel({"note": "Canceling the agreement due to user's request."}):
                print("Successfully cancelled the subscription.")
                # Actualizar los detalles del usuario en la base de datos
                user.is_subscribe = False
                user.subscription_status = SubscriptionStatus.objects.get(subscription_status="Cancelled")
                user.save()
                print("User's subscription details updated in the database.")
                return "Your subscription has been successfully cancelled. Do you need any further assistance?"
            else:
                print("Error: Could not cancel the subscription on PayPal.")
                return "There was an error cancelling your subscription with PayPal. Please try again later or contact support."
        else:
            print("User's subscription is not active or there was an issue accessing it.")
            return "Your subscription is not currently active or there was an issue accessing it."
    else:
        print("Error: Couldn't retrieve the Billing Agreement for subscription ID:", paypal_subscription_id)
        return "Couldn't retrieve your subscription details from PayPal."""
    
def cancel_subscription(subscription_id):
    # Obtener el token de acceso
    url = "https://api.sandbox.paypal.com/v1/oauth2/token"
    headers = {
        "Accept": "application/json",
        "Accept-Language": "en_US"
    }
    data = {
        "grant_type": "client_credentials"
    }
    auth = ("client_id", "client_secret")  # Reemplaza "client_id" y "client_secret" con tus propias credenciales de PayPal

    response = requests.post(url, headers=headers, data=data, auth=auth)

    if response.status_code == 200:
        response_data = response.json()
        access_token = response_data["access_token"]

        # Cancelar la suscripción
        url = f"https://api.sandbox.paypal.com/v1/billing/subscriptions/{subscription_id}/cancel"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {access_token}"
        }

        response = requests.post(url, headers=headers)

        if response.status_code == 204:
            print("La suscripción se ha cancelado exitosamente.")
            return "La suscripción se ha cancelado exitosamente."
        else:
            print("Error al cancelar la suscripción:", response.status_code, response.text)
            return "Error al cancelar la suscripción:"
    else:
        print("Error al obtener el token de acceso:", response.status_code, response.text)
        return "Error al obtener el token de acceso:"