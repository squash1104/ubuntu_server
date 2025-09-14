import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "sistema_fidelizacao.settings")

import django

django.setup()

from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application

import chat.routing
import chat.test_routing

# Get the Django ASGI application first
django_asgi_app = get_asgi_application()

# Combine both routing patterns
websocket_patterns = (
    chat.routing.websocket_urlpatterns + chat.test_routing.websocket_urlpatterns
)

application = ProtocolTypeRouter(
    {
        "http": django_asgi_app,
        "websocket": AuthMiddlewareStack(URLRouter(websocket_patterns)),
    }
)
