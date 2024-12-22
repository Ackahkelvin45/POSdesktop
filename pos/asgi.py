import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from dashboard.routing import websocket_urlpatterns as dashboard_patterns
from notifications.routing import websocket_urlpatterns as product_patterns

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pos.settings')

# Combine all WebSocket URL patterns
websocket_urlpatterns = dashboard_patterns + product_patterns

application = ProtocolTypeRouter({
    'http': get_asgi_application(),
    'websocket': AuthMiddlewareStack(
        URLRouter(websocket_urlpatterns)
    ),
})
