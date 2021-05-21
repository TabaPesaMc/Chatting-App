from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator
from channels.auth import AuthMiddlewareStack
import chat.routing

application = ProtocolTypeRouter({
    'websocket' : AllowedHostsOriginValidator(
        URLRouter(
            chat.routing.websocket_urlpatterns
        )
    )
})