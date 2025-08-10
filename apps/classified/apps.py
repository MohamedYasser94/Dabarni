from django.apps import AppConfig


class ClassifiedConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.classified'

    def ready(self):
        # Import the signals module so Django can discover the receivers
        import apps.classified.signals



