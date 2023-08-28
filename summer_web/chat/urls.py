from django.urls import path
from . import  views
# from .consumers  import ChatConsumer,MyConsumer
urlpatterns = [
    # 用于开启新的聊天室
    path('', views.index, name="index"),
    # 创建聊天室
    path('<room_name>/', views.room, name='room'),
    path("<str:room_name>/", views.room, name="room"),
]

# websocket_urlpatterns = [
#     path('ws/chat/<room_name>/', ChatConsumer.as_asgi()),
#     path('api/chat/<room_name>/', ChatConsumer.as_asgi()),
#     path('api/person/<client_id>/', MyConsumer.as_asgi()),
# ]