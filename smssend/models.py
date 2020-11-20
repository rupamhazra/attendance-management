from django.db import models

class SMSTemplate(models.Model):
    code=models.CharField(max_length=255)
    txt_content=models.TextField()
    contain_variable=models.TextField()
    is_test = models.BooleanField(default=False)

    class Meta:
        db_table = 'sms_template'

    def __str__(self):
        return self.code