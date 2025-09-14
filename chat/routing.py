# chat/routing.py
from django.urls import re_path

from . import consumers

websocket_urlpatterns = [
    re_path(r"ws/chat/(?P<username>\w+)/$", consumers.ChatConsumer.as_asgi()),
    re_path(r"ws/notify/$", consumers.NotifyConsumer.as_asgi()),
    re_path(r"ws/global/$", consumers.GlobalChatConsumer.as_asgi()),
]
