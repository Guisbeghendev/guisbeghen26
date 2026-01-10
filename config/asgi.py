import os
import django
from django.core.asgi import get_asgi_application

# 1. Define as configurações primeiro
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

# 2. Inicializa o Django
django.setup()

# 3. Importa o restante DEPOIS do django.setup()
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
import mensagens.routing
import suporte.routing
import repositorio.routing  # Importação do roteamento do repositório

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(
            mensagens.routing.websocket_urlpatterns +  # Rotas do Chat
            suporte.routing.websocket_urlpatterns +    # Rotas do Suporte
            repositorio.routing.websocket_urlpatterns  # Rotas do Repositório
        )
    ),
})