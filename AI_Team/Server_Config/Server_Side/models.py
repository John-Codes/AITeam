from django.db import models
from django.contrib.auth.models import AbstractUser

# Modelo para el estado de la suscripción
class Current_Plan(models.Model):
    current_plan = models.CharField(max_length=50)
    class Meta:
        app_label = 'Server_Side'

    def __str__(self):
        return self.current_plan
    
class SubscriptionStatus(models.Model):
    subscription_status = models.CharField(max_length=50)

    class Meta:
        app_label = 'Server_Side'

    def __str__(self):
        return self.subscription_status

# Modelo para el método de pago
class PaymentMethod(models.Model):
    method_pay = models.CharField(max_length=50)
    class Meta:
        app_label = 'Server_Side'

    def __str__(self):
        return self.method_pay

# Modelo de Usuario extendido
class Client(AbstractUser):
    class Meta:
        app_label = 'Server_Side'
        verbose_name_plural = "Clientes"

    def get_default_current_plan():
        return Current_Plan.objects.get(id=1).id

    def get_default_subscription_status():
        return SubscriptionStatus.objects.get(id=1).id

    def get_default_payment_method():
        return PaymentMethod.objects.get(id=1).id

    is_subscribe = models.BooleanField(default=False)
    order_id = models.CharField(max_length=255, null=True, blank=True)
    last_transaction_status = models.CharField(max_length=50, null=True, blank=True)
    current_plan = models.ForeignKey(Current_Plan, on_delete=models.CASCADE, default=get_default_current_plan)
    subscription_status = models.ForeignKey(SubscriptionStatus, on_delete=models.CASCADE, default=get_default_subscription_status)
    id_pay = models.PositiveIntegerField(null=True, blank=True)
    method_pay = models.ForeignKey(PaymentMethod, on_delete=models.CASCADE, default=get_default_payment_method)
    next_date_pay = models.DateField(null=True, blank=True)
    date_subscription = models.DateField(null=True, blank=True) 

    def __str__(self):
        return self.username

class ClienContext(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    context = models.TextField(max_length=None)