from django.contrib import admin
from .models import Plan,Membership,Server

# Register your models here.

admin.site.register(Plan)
admin.site.register(Membership)
admin.site.register(Server)