from django.urls import re_path
from . import test_consumer

websocket_urlpatterns = [
    re_path(r"^ws/test/(?P<username>[\w.@+-]+)/$", test_consumer.TestChatConsumer.as_asgi()),
]
