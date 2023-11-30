from django.contrib import admin
from django.utils.html import format_html
from .models import Client, SubscriptionDetail, ClienContext

class SubscriptionDetailAdmin(admin.ModelAdmin):
    list_display = ('name', 'product_name', 'plan_name', 'price', 'subscription_date', 'code', 'features_list','market_place')
    search_fields = ('name', 'product_name', 'plan_name', 'code')
    list_filter = ('price', 'subscription_date')

# Administrador para Client
class ClientAdmin(admin.ModelAdmin):
    list_display = [
        'email', 'is_subscribe', 'next_date_pay', 'date_subscription', 'total_tokens', 'change_password'
    ]

    search_fields = ['email']
    list_filter = ('is_subscribe',)
    ordering = ('email',)

    
    def change_password(self, obj):
        return format_html('<a href="../password/{}/change/">Change Password</a>', obj.id)
    change_password.short_description = 'Change Password'

class ClienContextAdmin(admin.ModelAdmin):
    list_display = ('client', 'context')
    search_fields = ('client__email', 'context')
    list_filter = ('client',)


# Registrar modelos
admin.site.register(ClienContext, ClienContextAdmin)
admin.site.register(SubscriptionDetail, SubscriptionDetailAdmin)
admin.site.register(Client, ClientAdmin)