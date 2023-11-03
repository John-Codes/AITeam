import paypalrestsdk
from django.contrib import messages
from paypal.standard.ipn.models import PayPalIPN
from paypalrestsdk import BillingAgreement
from Server_Config.Server_Side.models import SubscriptionStatus
from django.conf import settings

paypalrestsdk.configure({
    "mode": "sandbox",  # Puedes cambiar esto a "live" cuando vayas a producción
    "client_id": settings.PCI,
    "client_secret": settings.PCS
    })

def cancel_subscription(user):
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
        return "Couldn't retrieve your subscription details from PayPal."