from django.contrib import admin
from .models import EmailToken, NewsLetter, Plan, Membership, Server, Blog, Contact




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
        'expiration_data','created_at'
                   ]
    list_filter=[
        'user', 'premium_membership',
        'payment_completed', 'cancel_membership',
        'expiration_data' , 'subscription_date'
        ]
    list_per_page = 20
    search_fields =['user','subscription_date', 'expiration_data']



class ServerAdmin(admin.ModelAdmin):
    list_display =['server_name', 'region', 'hostname', 'server_username', 'flag_code', 'premium_server', 'created_at']
    list_filter=['flag_code', 'premium_server', 'region']
    list_per_page = 20
    search_fields = ['server_username', 'server_name']


class NewsLetterAdmin(admin.ModelAdmin):
    list_display = ["id", 'email', 'created_at']


class EmailTokenAdmin(admin.ModelAdmin):
    readonly_fields = ["user", 'token', 'expired', 'expiration_time', 'created_at']


class BlogAdmin(admin.ModelAdmin):
    list_display = ["title", 'slug', 'created_at', 'updated_at', 'image_tag']
    list_filter = ['created_at', 'updated_at']
    search_fields = ['title', 'slug']
    list_per_page =10


class ContactAdmin(admin.ModelAdmin):
    list_display = ["name", 'email', 'subject', 'message', 'created_at']
    list_filter = ['created_at']
    list_per_page =50


admin.site.register(Plan, PlanAdmin)
admin.site.register(Membership, MembershipAdmin)
admin.site.register(Server, ServerAdmin)
admin.site.register(NewsLetter, NewsLetterAdmin)
admin.site.register(EmailToken, EmailTokenAdmin)
admin.site.register(Blog, BlogAdmin)
admin.site.register(Contact, ContactAdmin)