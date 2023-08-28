from django.urls import re_path

from . import consumers

websocket_urlpatterns = [
    re_path(r"ws/chat/(?P<room_name>\w+)/$", consumers.ChatConsumer.as_asgi()),
    re_path(r"api/chat/(?P<room_name>\w+)/$", consumers.ChatConsumer.as_asgi()),
    re_path(r"ws/person/(?P<email>[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)/$", consumers.MyConsumer.as_asgi()),
    re_path(r"api/person/(?P<email>[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)/$", consumers.MyConsumer.as_asgi()),
    re_path(r"ws/person/(?P<email>\w+)/$", consumers.MyConsumer.as_asgi()),
    re_path(r"api/person/(?P<email>\w+)/$", consumers.MyConsumer.as_asgi()),
]