from django.contrib import admin
from django.utils.html import format_html
from .models import Client, CurrentPlan, SubscriptionStatus, PaymentMethod

# Administrador para CurrentPlan
class CurrentPlanAdmin(admin.ModelAdmin):
    list_display = ['current_plan']
    search_fields = ['current_plan']

# Administrador para SubscriptionStatus
class SubscriptionStatusAdmin(admin.ModelAdmin):
    list_display = ['subscription_status']
    search_fields = ['subscription_status']

# Administrador para PaymentMethod
class PaymentMethodAdmin(admin.ModelAdmin):
    list_display = ['method_pay']
    search_fields = ['method_pay']

# Administrador para Client
class ClientAdmin(admin.ModelAdmin):
    list_display = [
        'username', 'email', 'is_subscribe', 'get_current_plan', 'get_subscription_status',
        'id_pay', 'get_method_pay', 'next_date_pay', 'date_subscription', 'change_password'
    ]

    def get_current_plan(self, obj):
        return obj.current_plan.current_plan
    get_current_plan.short_description = 'Current Plan'

    def get_subscription_status(self, obj):
        return obj.subscription_status.subscription_status
    get_subscription_status.short_description = 'Subscription Status'

    def get_method_pay(self, obj):
        return obj.method_pay.method_pay
    get_method_pay.short_description = 'Payment Method'

    list_display = [
        'username', 'email', 'is_subscribe', 'current_plan', 'subscription_status',
        'id_pay', 'method_pay', 'next_date_pay', 'date_subscription', 'change_password'
    ]
    search_fields = ('username', 'email')
    list_filter = ('is_subscribe', 'current_plan', 'subscription_status', 'method_pay')
    ordering = ('username',)

    def change_password(self, obj):
        return format_html('<a href="../password/{}/change/">Change Password</a>', obj.id)
    change_password.short_description = 'Change Password'

# Registrar modelos
admin.site.register(CurrentPlan, CurrentPlanAdmin)
admin.site.register(SubscriptionStatus, SubscriptionStatusAdmin)
admin.site.register(PaymentMethod, PaymentMethodAdmin)
admin.site.register(Client, ClientAdmin)
