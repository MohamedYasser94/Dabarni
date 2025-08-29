from django.apps import AppConfig
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from rest_framework import serializers




class UserConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'user'






