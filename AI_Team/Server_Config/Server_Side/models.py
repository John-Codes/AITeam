from django.db import models
from django.contrib.auth.models import AbstractUser
import json
import string
import random
from django.db import models
#from django.contrib.postgres.fields import JSONField # Para cuando se trabaje con postgres

def generate_random_code():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))

class SubscriptionDetail(models.Model):
    STATUS_CHOICES = [
        ('Active', 'Active'),
        ('Inactive', 'Inactive'),
        ('Pending', 'Pending'),
        ('Cancelled', 'Cancelled'),
        # Añade más estados según sea necesario
    ]

    product_name = models.CharField(max_length=200)
    product_id = models.CharField(max_length=200)
    plan_name = models.CharField(max_length=200)
    plan_id = models.CharField(max_length=200)
    name = models.CharField(max_length=200)  # Este era el 'subscription_name'
    code = models.CharField(max_length=5, default=generate_random_code)
    price = models.FloatField()
    subscription_date = models.DateField() 
    features_list = models.TextField(default=json.dumps([]))  # Guarda la lista de características como JSON
    market_place = models.TextField(default=json.dumps([]))   # Guarda la lista de mercados como JSON
    #features_list = JSONField(default=list)  # Para cuando se trabaje con postgres
    #market_place = JSONField(default=list)  # Para cuando se trabaje con postgres

    def __str__(self):
        return self.name

class Client(AbstractUser):
    is_subscribe = models.BooleanField(default=False)
    subscription_detail = models.ForeignKey(SubscriptionDetail, on_delete=models.SET_NULL, null=True, blank=True)
    order_id = models.CharField(max_length=100, null=True, blank=True)
    last_transaction_status = models.CharField(max_length=50, null=True, blank=True)
    status_subscription = models.CharField(max_length=50, default='Inactive')
    next_date_pay = models.DateField(null=True, blank=True)
    date_subscription = models.DateField(null=True, blank=True) 
    total_tokens = models.PositiveIntegerField(null=True, blank=True, default=0)

    def __str__(self):
        return self.username

    class Meta:
        app_label = 'Server_Side'
        verbose_name_plural = "Clientes"


class ClienContext(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    context = models.TextField(max_length=None)

    def __str__(self):
        return self.context