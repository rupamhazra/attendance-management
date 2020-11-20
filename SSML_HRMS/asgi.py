import os

from django.core.asgi import get_asgi_application

os.environ.setdefault('SERVER_GATEWAY_INTERFACE', 'Asynchronous')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'SSML_HRMS.settings')

application = get_asgi_application()