from django.apps import AppConfig


class PrescriptionsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'prescriptions'
    verbose_name = 'Reseptlər'

    def ready(self):
        from . import signals  # noqa

