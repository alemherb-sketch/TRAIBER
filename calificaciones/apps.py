from django.apps import AppConfig


class CalificacionesConfig(AppConfig):
    name = 'calificaciones'

    def ready(self):
        from . import signals  # noqa: F401
