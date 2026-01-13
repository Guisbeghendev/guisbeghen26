from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    # Ajustado para aceitar caracteres alfanuméricos e hifens do slug
    re_path(r'^ws/galeria/(?P<slug>[\w-]+)/$', consumers.GaleriaConsumer.as_asgi()),
]