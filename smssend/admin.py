from django.contrib import admin

from smssend.models import *

@admin.register(SMSTemplate)
class SMSTemplate(admin.ModelAdmin):
    list_display = [field.name for field in SMSTemplate._meta.fields]
