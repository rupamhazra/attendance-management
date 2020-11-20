from django.contrib import admin

from history.models import *


@admin.register(ActionHistory)
class ActionHistory(admin.ModelAdmin):
    list_display = [field.name for field in ActionHistory._meta.fields]
    search_fields = ('module_name', 'url', 'action_by_id')
