# repositorio/routing.py

from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/galeria/(?P<slug>[\w-]+)/$', consumers.GaleriaConsumer.as_asgi()),
]