import os
import django
from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
import mensagens.routing
import suporte.routing
import repositorio.routing

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(
            mensagens.routing.websocket_urlpatterns +
            suporte.routing.websocket_urlpatterns +
            repositorio.routing.websocket_urlpatterns
        )
    ),
})