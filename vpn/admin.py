from django.contrib import admin
from .models import Plan,Membership,Server

# Register your models here.
class PlanAdmin(admin.ModelAdmin):
    list_display =['id', 'title', 'price', 'plan_duration_months']
    list_filter=['title', 'price']
    list_per_page =10
    search_fields =['title', 'price']


class MembershipAdmin(admin.ModelAdmin):
    list_display =[
        'id', 'user', 'plans',
        'premium_membership', 'payment_completed',
        'cancel_membership', 'subscription_date',
        'expiration_data'
                   ]
    list_filter=[
        'user', 'premium_membership',
        'payment_completed', 'cancel_membership',
        'expiration_data' , 'subscription_date'
        ]
    list_per_page = 50
    search_fields =['user','subscription_date', 'expiration_data']

class ServerAdmin(admin.ModelAdmin):
    list_display =['server_name', 'region', 'hostname', 'server_username', 'flag_code', 'premium_server']
    list_filter=['flag_code', 'premium_server', 'region']
    list_per_page = 50
    search_fields = ['server_username', 'server_name']


admin.site.register(Plan, PlanAdmin)
admin.site.register(Membership, MembershipAdmin)
admin.site.register(Server, ServerAdmin)