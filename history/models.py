from django.db import models
#from django.contrib.auth.models import User
from datetime import datetime
from django.conf import settings


class ActionHistory(models.Model):
    type = (
        ('Admin', 'Admin'),
        ('API', 'API')
    )
    action_type = (
        ('Create', 'Create'),
        ('Update', 'Update'),
        ('Delete','Delete')
    )
    module_name = models.CharField(max_length=255)
    action_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='history_action_user', blank=True, null=True)
    action_date = models.DateTimeField(default=datetime.now)
    action = models.CharField(choices=action_type,max_length=255)
    url = models.TextField()
    previous_data = models.TextField(null=True, blank=True)
    current_data = models.TextField(null=True, blank=True)
    is_deleted = models.BooleanField(default=False)
    mode = models.CharField(max_length=100,choices=type,default='API')

    def __str__(self):
        return str(self.id)

    class Meta:
        db_table = 'action_history'
