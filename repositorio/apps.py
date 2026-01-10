from django.apps import AppConfig

class RepositorioConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'repositorio'

    def ready(self):
        import repositorio.signals