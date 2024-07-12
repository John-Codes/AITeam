
# class Subscription(View):
#     template_name = "subscription.html"
    
#     def get(self, request, *args, **kwargs):
#         """
#         Render the subscription page with all plan details.
#         """
        
#         context = {
#             "plans": plans_data,  # Cambiado a "plans" para que sea más claro en el template
#             "user": request.user,
#             'STRIPE_PUBLIC_KEY': settings.STRIPE_PUBLIC_KEY,
#         }

#         return render(request, self.template_name, context)
    
# def SubscriptionCheckout(request, plan_id):
#     print(f"SubscriptionCheckout function called with plan_id {plan_id}")
#     # Asegúrate de que plan_id es un índice válido en plans_data
#     plan = plans_data[plan_id]

#     host = request.get_host()
#     invoice_id = uuid.uuid4()
#     # Creamos el diccionario para la suscripción
#     paypal_dict = {
#         "cmd": "_xclick-subscriptions",
#         "business": settings.PAYPAL_RECEIVER_EMAIL,
#         "a3": plan['amount'] / 100,     # Precio mensual. Convertimos de centavos a dólares
#         "p3": 1,                        # Duración de cada unidad (en este caso, meses)
#         "t3": "M",                      # Unidad de duración ("M" para Mes)
#         "src": "1",                     # Hacer pagos recurrentes
#         "sra": "1",                     # Reintentar pago en caso de error
#         "no_note": "1",                 # Quitar notas adicionales
#         "item_name": plan['name'],
#         "invoice": str(invoice_id),
#         "notify_url": f"http://{host}{reverse('paypal-ipn')}",
#         "return": f"http://{host}{reverse('payment_success', kwargs={'plan_id': plan_id})}",
#         "cancel_return": f"http://{host}{reverse('payment_failed', kwargs={'plan_id': plan_id})}",
#     }

#     paypal_form = PayPalPaymentsForm(initial=paypal_dict, button_type="subscribe")

#     context = {
#         'plan': plan,
#         'paypal': paypal_form
#     }
#     print(f"Creating a subscription checkout for invoice {invoice_id}")
#     request.session['invoice'] = str(invoice_id)
#     return render(request, 'payment/subscription_checkout.html', context)

# def PaymentSuccessful(request, plan_id):
#     print(f"PaymentSuccessful function called with plan_id {plan_id}")
#     print('payment successful')
#     plan = plans_data[plan_id]
#     plan['amount'] = plan['amount'] / 100
#     user = request.user 
#     invoice = request.session.get('invoice')
#     print('invoice id uuid', invoice)
#     print('Attempting to retrieve IPN object for invoice id uuid:', invoice)

#     # Intenta encontrar el objeto PayPalIPN usando el invoice (uuid)
#     try:
#         ipn_obj = PayPalIPN.objects.filter(invoice=invoice, payment_status="Completed").first()
#         all_registers = PayPalIPN.objects.all()
#         print(f"Found {len(all_registers)} PayPalIPN objects")
#         if ipn_obj:
#             print(f"Found PayPalIPN object with invoice {invoice} and payment_status 'Completed'")
#             print(f"Payment date: {ipn_obj.payment_date}, Payment status: {ipn_obj.payment_status}")
#         else:
#             print(f"No PayPalIPN object found with invoice {invoice} and payment_status 'Completed'")
#         paypal_subscription_id = ipn_obj.subscr_id if ipn_obj else 0
#     except PayPalIPN.DoesNotExist:
#         print(f"PayPalIPN object does not exist for invoice {invoice}")
#         paypal_subscription_id = 0

#     # Actualizar datos del modelo del usuario
#     print(user)
#     user.is_subscribe = True
#     print('paypal subscription id',paypal_subscription_id)
#     user.order_id = paypal_subscription_id
#     print('add the id to the user',user.order_id)
#     user.last_transaction_status = "Success"
#     user.current_plan = Current_Plan.objects.get(current_plan=plan['name'])  
#     user.subscription_status = SubscriptionStatus.objects.get(subscription_status="Active")
#     user.method_pay = PaymentMethod.objects.get(method_pay="Paypal")
#     user.next_date_pay = datetime.now() + timedelta(days=30)  # Asume un plan mensual
#     user.date_subscription = datetime.now()
#     user.save()

#     return render(request, 'payment/payment_success.html', {'plan': plan})


# def PaymentFailed(request, plan_id):
#     print(f"PaymentFailed function called with plan_id {plan_id}")
#     plan = plans_data[plan_id]
#     return render(request, 'payment/payment_failed.html', {'plan': plan})