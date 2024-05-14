import os
import requests
from datetime import datetime
from datetime import timedelta
from django.urls import reverse
from Server_Config.Server_Side.models import SubscriptionDetail
def generate_access_token():
    # client_id = 'AThJhSpO1NlOyyx19jAC5Vb2CStnbrurdgm3hqKzVaVoz85T9lKKoYThf7hKRNYeovC6b_iJOgkXZCMB'  # Replace with your PayPal client ID
    # client_secret = 'ECk7V4Ntt5PJy4Nosm9g80gMzf2WMvwVptzlmwOzEsxz37FPM_NXa6rCFH8BcR4Mc24odULhHM2eH5Aw'  # Replace with your PayPal client secret
    # token_url = 'https://api.sandbox.paypal.com/v1/oauth2/token'
    client_id = os.getenv('PCI')
    client_secret = os.getenv('PCS')
    token_url = 'https://api.paypal.com/v1/oauth2/token'

    response = requests.post(token_url, auth=(client_id, client_secret), data={'grant_type': 'client_credentials'})

    if response.status_code == 200:
        access_token = response.json().get('access_token')
        return access_token
    else:
        print(f"Error: {response.status_code}")
        print(f"Response: {response.text}")
        return None
    

def create_product(request, access_token):
    error_message = None
    product_name = request.POST.get('product_name')
    description = request.POST.get('description')
    product_payload = {
        "name": product_name,
        "type": "SERVICE",
        "category": "SOFTWARE",
        "description": description
        # Add other product details as needed
    }

    product_response = requests.post(
        'https://api.paypal.com/v1/catalogs/products',
        json=product_payload,
        headers={
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {access_token}'
        }
    )
    return product_response


def create_plan(request, access_token, product_id, price):
    print("into to create_plan")
    error_message = None
    plan_name = request.POST.get('plan_name')
    plan_payload = {
        "product_id": product_id,
        "name": plan_name,
        "billing_cycles": [
            {
                "tenure_type": "TRIAL",
                "sequence": 1,
                "frequency": {
                    "interval_unit": "MONTH",
                    "interval_count": 1
                },
                "total_cycles": 2,
                "pricing_scheme": {
                    "fixed_price": {
                        "value": "3",
                        "currency_code": "USD"
                    }
                }
            },
            {
                "frequency": {
                    "interval_unit": "MONTH",
                    "interval_count": 1
                },
                "tenure_type": "TRIAL",
                "sequence": 2,
                "total_cycles": 3,
                "pricing_scheme": {
                    "fixed_price": {
                        "value": str(price),
                        "currency_code": "USD"
                    }
                }
            },
            {
                "frequency": {
                    "interval_unit": "MONTH",
                    "interval_count": 1
                },
                "tenure_type": "REGULAR",
                "sequence": 3,
                "total_cycles": 12,
                "pricing_scheme": {
                    "fixed_price": {
                        "value": str(price),
                        "currency_code": "USD"
                    }
                }
            }
        ],
        "payment_preferences": {
            "auto_bill_outstanding": 1,
            "setup_fee": {
                "value": str(price),
                "currency_code": "USD"
            },
            "setup_fee_failure_action": "CONTINUE",
            "payment_failure_threshold": 3
        },
        "description": plan_name,
        "status": "ACTIVE",
        "taxes": {
            "percentage": "10",
            "inclusive": 0
        }
    }

    plan_response = requests.post(
        'https://api.paypal.com/v1/billing/plans',
        json=plan_payload,
        headers={
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {access_token}'
        }
    )
    print("plan_response")
    print(plan_response)
    return plan_response


def create_subscription_agreement(request, access_token, plan_id):
    print(request)
    error_message = None

    subscription =  SubscriptionDetail.objects.get(plan_id=plan_id) #request.POST.get('subscription_name')
    subscription_name = subscription.name
    print(subscription_name)
    subscription_date = request.POST.get('date', datetime.now().strftime('%Y-%m-%d'))
    subscription_start_date = datetime.strptime(subscription_date, '%Y-%m-%d') + timedelta(minutes=5)

    return_url = request.build_absolute_uri(reverse('payment_success', args=[plan_id]))
    cancel_url = request.build_absolute_uri(reverse('payment_failed', args=[plan_id]))


    # Use the pre-approved sandbox business account email
    payer_email = "Efexzium@gmail.com"  # Replace with the pre-approved sandbox business account email

    billing_agreement_token = request.POST.get('billing_agreement_token')
    print(billing_agreement_token)
    agreement_payload = {
        "name": subscription_name,
        "description": "Subscription agreement for the sample plan",
        "start_date": subscription_start_date.isoformat(),
        "plan_id": plan_id,
        "payer": {
            "payment_method": "paypal",
            "payer_info": {
                "email": payer_email
            }
        },
        "shipping_address": {
             "line1": "Domenench ave 400 suit 207",
             "city": "San Juan",
             "state": "PR",
             "postal_code": "00918",
             "country_code": "US"
         },
        "application_context": {
            "brand_name": "Efexzium",
            "shipping_preference": "NO_SHIPPING",  # Important for SaaS
            "user_action": "SUBSCRIBE_NOW",
            "payment_method": {
                "payer_selected": "PAYPAL",
                "payee_preferred": "IMMEDIATE_PAYMENT_REQUIRED"
            },

            "return_url": return_url,
            "cancel_url": cancel_url
        },
        "billing_agreement_tokens": [
            {
                "token_id": billing_agreement_token,  # Use the provided billing agreement token
                "description": "Pre-approved billing agreement"
            }
        ]
    }
    # agreement_payload = {
    #     "name": subscription_name,
    #     "description": "Subscription agreement for the sample plan",
    #     "start_date": subscription_start_date.isoformat(),
    #     "plan_id": plan_id,
    #     "payer": {
    #         "payment_method": "paypal",
    #         "payer_info": {
    #             "email": company_email
    #         }
    #     },
    #     "shipping_address": {
    #         "line1": "1234 Main St",
    #         "city": "San Jose",
    #         "state": "CA",
    #         "postal_code": "95131",
    #         "country_code": "US"
    #     },
    #     "application_context": {
    #         "return_url": return_url,
    #         "cancel_url": cancel_url
    #     },
    #     "billing_agreement_tokens": [
    #         {
    #             "token_id": billing_agreement_token,  # Use the provided billing agreement token
    #             "description": "Pre-approved billing agreement"
    #         }
    #     ]
    # }

    agreement_response = requests.post(
        'https://api.paypal.com/v1/billing/subscriptions',
        json=agreement_payload,
        headers={
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {access_token}'
        }
    )
    print("agreement_response", agreement_response)
    return agreement_response