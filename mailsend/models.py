from django.db import models

class MailTemplate(models.Model):
    name = models.CharField(max_length=255)
    code = models.CharField(max_length=255)
    subject = models.CharField(max_length=255)
    html_content = models.TextField()
    template_variable = models.TextField()
    is_test = models.BooleanField(default=False)

    class Meta:
        db_table = 'mail_template'

    def __str__(self):
        return self.name

# added by Shubhadeep to implement email service

class MailHistory(models.Model):
    status_choices = (
                ('pending', 'pending'),
                ('sent', 'sent'),
                ('error','error'),)

    code = models.CharField(max_length=255)
    timestamp = models.DateTimeField(auto_now_add=True, null=True)
    recipient_list = models.TextField(null=True)
    subject = models.TextField(null=True)
    body = models.TextField(null=True)
    attachment = models.TextField(choices=status_choices, default='pending')
    status = models.CharField(max_length=30)
    error_msg = models.TextField(default='')

    class Meta:
        db_table = 'mail_history'

    def __str__(self):
        return self.code

# --
