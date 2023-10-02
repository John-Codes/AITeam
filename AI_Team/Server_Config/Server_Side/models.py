from django.db import models
from django.contrib.auth.models import AbstractUser

# Modelo para el estado de la suscripción
class CurrentPlan(models.Model):
    current_plan = models.CharField(max_length=50)

    def __str__(self):
        return self.current_plan
    
class SubscriptionStatus(models.Model):
    subscription_status = models.CharField(max_length=50)

    def __str__(self):
        return self.subscription_status

# Modelo para el método de pago
class PaymentMethod(models.Model):
    method_pay = models.CharField(max_length=50)

    def __str__(self):
        return self.method_pay

# Modelo de Usuario extendido
class Client(AbstractUser):
    class Meta:
        app_label = 'Server_Side'
        verbose_name_plural = "Clientes" 

    is_subscribe = models.BooleanField(default=False)
    current_plan = models.ForeignKey(CurrentPlan, on_delete=models.CASCADE, default=1)
    subscription_status = models.ForeignKey(SubscriptionStatus, on_delete=models.CASCADE, default=1)
    id_pay = models.PositiveIntegerField(null=True, blank=True)
    method_pay = models.ForeignKey(PaymentMethod, on_delete=models.CASCADE, default=1)
    next_date_pay = models.DateField(null=True, blank=True)
    date_subscription = models.DateField(null=True, blank=True)

    def __str__(self):
        return self.username
 