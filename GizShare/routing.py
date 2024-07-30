from asgiref.sync import sync_to_async
from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from django.urls import path
from django.core.asgi import get_asgi_application
from rest_framework_simplejwt.backends import TokenBackend
from user.models import User
from chat import consume

websocket_urlpatterns = [
    path('ws/chat/', consume.ChatConsumer.as_asgi()),
]


@sync_to_async
def get_user(user):
    if user:
        try:
            return User.objects.select_related('userprofile').get(id=user)
        except User.DoesNotExist as error:
            print(error, 'erorr')
            return None
    else:
        return None


class TokenAuthMiddleware:
    """
    Token authorization middleware for Django Channels 2
    """

    def __init__(self, inner):
        print(inner)
        self.inner = inner

    async def __call__(self, scope, receive, send):
        headers = dict(scope['headers'])
        if b'authorization' in headers:
            token_key = headers[b'authorization']
            if token_key:
                try:
                    valid_data = TokenBackend(algorithm='HS256').decode(token_key, verify=False)
                    scope['user'] = await get_user(valid_data['user_id'])
                except Exception as v:
                    print('error', v)

        return await self.inner(scope, receive, send)


# Handy shortcut for applying all three layers at once
def TokenAuthMiddlewareStack(inner):
    print(inner, "inner")
    return TokenAuthMiddleware(AuthMiddlewareStack(inner))


application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": TokenAuthMiddlewareStack(
        URLRouter(
            websocket_urlpatterns
        )
    )
})
