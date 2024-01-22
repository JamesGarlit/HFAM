"""
WSGI config for HyFAS project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/howto/deployment/wsgi/
"""
import os

from django.core.wsgi import get_wsgi_application

settings_module = 'HyFAS.deplyoment' if 'WEBSITE_HOSTNAME' in os.environ else 'HyFAS.settings'

os.environ.setdefault('DJANGO_SETTINGS_MODULE', settings_module)
# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'HyFAS.settings')

application = get_wsgi_application()
