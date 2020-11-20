import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('SERVER_GATEWAY_INTERFACE', 'Web')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'SSML_HRMS.settings')

application = get_wsgi_application()
