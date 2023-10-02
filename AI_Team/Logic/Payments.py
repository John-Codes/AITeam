import paypalrestsdk

# Configuración de PayPal
paypalrestsdk.configure({
  "mode": "sandbox",  # Puedes cambiar esto a "live" cuando vayas a producción
  "client_id": "AT0E7B7zOA8Se5phnmPOc0ktRyj4IwaC4rMi9z6I5roenJcGhMJBQnSWKAcGxYwivBf-43Uo-KwN6MOs",
  "client_secret": "EL2ut_dNjkzX42cq2LFZEpLoA7Y0GtcZTG1QUO9zU0pgX_Qg70a7RGIoIBXOWuQudrL5e9c6j1Z_dUFm"
})

def create_paypal_payment(plan):
    """Crea un pago de PayPal y devuelve la URL de aprobación"""
    payment = paypalrestsdk.Payment({
        "intent": "sale",
        "payer": {
            "payment_method": "paypal"
        },
        "redirect_urls": {
            "return_url": "http://127.0.0.1:8000/payment/success/",
            "cancel_url": "http://127.0.0.1:8000/payment/failed/"
        },
        "transactions": [{
            "item_list": {
                "items": [{
                    "name": plan['name'],
                    "sku": plan['invoice'],
                    "price": str(plan['amount']),
                    "currency": "USD",
                    "quantity": 1
                }]
            },
            "amount": {
                "total": str(plan['amount']),
                "currency": "USD"
            },
            "description": plan['description']
        }]
    })

    if payment.create():
        for link in payment.links:
            if link.rel == "approval_url":
                return link.href

    return None

def create_stripe_payment():
    plans = [
        {
        'name': 'Plan Name 1',
        'amount': 10.00,
        'description': 'you can obtain access to Admin Panel and create a page with AI',
        'invoice': 'invoice-plan-1'
        },
        {
        'name': 'Plan Name 2',
        'amount': 20.00,
        'description': 'You can create 5 pages with our AI',
        'invoice': 'invoice-plan-2'
        },
        {
        'name': 'Plan Name 3',
        'amount': 40.00,
        'description': 'Access to our VSCode Extension and use it',
        'invoice': 'invoice-plan-3'
        }
        ]
    
    return plans