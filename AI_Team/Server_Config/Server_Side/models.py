from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
import json
import string
import random
from django.db import models
#from django.contrib.postgres.fields import JSONField # Para cuando se trabaje con postgres

class UserCongifuration(BaseUserManager):
    def create_user(self, email, password=None):
        if not email:
            raise ValueError('Users must have an email address')

        user = self.model(
            email=self.normalize_email(email),
        )

        user.set_password(password)
        user.is_active = True  # Los usuarios estarán activos por defecto
        user.is_staff = False  # Los usuarios no serán staff por defecto
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None):
        user = self.create_user(
            email,
            password=password,
        )
        user.is_admin = True
        user.is_staff = True
        user.is_active = True
        user.save(using=self._db)
        return user
    
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

class Client(AbstractBaseUser):
    email = models.EmailField(
        verbose_name='email address',
        max_length=255,
        unique=True,
    )
    is_subscribe = models.BooleanField(default=False)
    subscription_detail = models.ForeignKey(SubscriptionDetail, on_delete=models.SET_NULL, null=True, blank=True)
    order_id = models.CharField(max_length=100, null=True, blank=True)
    last_transaction_status = models.CharField(max_length=50, null=True, blank=True)
    status_subscription = models.CharField(max_length=50, default='Inactive')
    next_date_pay = models.DateField(null=True, blank=True)
    date_subscription = models.DateField(null=True, blank=True) 
    total_tokens = models.PositiveIntegerField(null=True, blank=True, default=0)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    objects = UserCongifuration()
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

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
    
class ChatInfo(models.Model):
    title = models.CharField(max_length=200)
    header = models.CharField(max_length=200)
    description = models.TextField()
    default_message = models.TextField()

class Keyword(models.Model):
    general_info = models.ForeignKey(ChatInfo, related_name='keywords', on_delete=models.CASCADE)
    keyword = models.CharField(max_length=100)

class ListItem(models.Model):
    general_info = models.ForeignKey(ChatInfo, related_name='list_items', on_delete=models.CASCADE)
    text = models.CharField(max_length=100)
    url = models.URLField()

class Product(models.Model):
    general_info = models.ForeignKey(ChatInfo, related_name='products', on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    description = models.TextField()
    value = models.CharField(max_length=100)
    url = models.URLField()