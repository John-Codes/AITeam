from django.contrib import messages
import requests
from django.conf import settings
import requests
from django.shortcuts import redirect, get_object_or_404
from Server_Config.Server_Side.models import Client as User
def generate_access_token():    
    # GET A variable from django.conf.settings
    client_id = settings.PCI
    client_secret = settings.PCS
    print('client_id', client_id)
    print('client_secret', client_secret)
    #token_url_debug = 'https://api.sandbox.paypal.com/v1/oauth2/token'
    token_url_production = 'https://api.paypal.com/v1/oauth2/token'

    response = requests.post(token_url_production, auth=(client_id, client_secret), data={'grant_type': 'client_credentials'})

    if response.status_code == 200:
        access_token = response.json().get('access_token')
        return access_token
    else:
        return None
def cancel_subscription(request, order_id):
    if order_id:
        user = User.objects.get(order_id=order_id)
    else:
        # De lo contrario, el usuario está cancelando su propia suscripción
        user = request.user
    user = request.user
    access_token = generate_access_token()
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {access_token}'
    }
    #paypal_api_endpoint_debug = 'https://api.sandbox.paypal.com'
    paypal_api_endpoint_production = 'https://api.paypal.com'

    cancel_subscription_response = requests.post(
        f'{paypal_api_endpoint_production}/v1/billing/subscriptions/{user.order_id}/cancel',
        headers=headers
    )

    if cancel_subscription_response.status_code == 204:
        user.is_subscribe = False  # Actualizar el estado de suscripción
        user.last_transaction_status = 'CANCELED'
        user.status_subscription = 'Inactive'  # Suponiendo que agregues este campo
        user.save()
        return 'Subscription canceled successfully.'
    else:
        error_message = f"Failed to cancel subscription. PayPal API Response: {cancel_subscription_response.status_code} - {cancel_subscription_response.text}"
        return error_message