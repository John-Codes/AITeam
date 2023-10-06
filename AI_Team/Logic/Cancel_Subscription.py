import paypalrestsdk
from django.contrib import messages
from paypal.standard.ipn.models import PayPalIPN
from paypalrestsdk import BillingAgreement
from Server_Config.Server_Side.models import SubscriptionStatus
from django.conf import settings


paypalrestsdk.configure({
    "mode": "sandbox",  # Puedes cambiar esto a "live" cuando vayas a producción
    "client_id": 'AQMIrYAiPvK-xGhOlI3k05qwaekR81F85JIor0S0iMMgyMvXwDbB1lGwAHIfYw5abnmQDJIAr70m-QKC',
    "client_secret": 'ENzXZs1hIYTolXArxx4q0lLMsb4rg4S9DmlwEJbyepMpVR-uRhiHwiJphoYt1pO_wMuMXBdK-9zd8xoo'
    })

def cancel_subscription(user):
    print(settings.PCI, settings.PCS)
    # Obtener el ID de la suscripción de PayPal
    paypal_subscription_id = user.order_id

    if not paypal_subscription_id:
        return "Couldn't find your subscription details."

    try:
        agreement = BillingAgreement.find(paypal_subscription_id)
    except Exception as e:
        print("Error al obtener el acuerdo:", e)
        return str(e)

    if agreement:
        if agreement.state == "Active":
            if agreement.cancel({"note": "Canceling the agreement due to user's request."}):
                # Actualizar los detalles del usuario en la base de datos
                user.is_subscribe = False
                user.subscription_status = SubscriptionStatus.objects.get(subscription_status="Cancelled")
                user.save()
                return "Your subscription has been successfully cancelled. Do you need any further assistance?"
            else:
                return "There was an error cancelling your subscription with PayPal. Please try again later or contact support."
        else:
            return "Your subscription is not currently active or there was an issue accessing it."
    else:
        return "Couldn't retrieve your subscription details from PayPal."
