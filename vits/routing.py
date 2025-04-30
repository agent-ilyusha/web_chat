from django.urls import re_path, path
from chat.consumers import ChatConsumer
from video_message.consumers import VideoChatConsumer

websocket_urlpatterns = [
    re_path(r'ws/chat/(?P<room_name>\w+)/$', ChatConsumer.as_asgi()),
    re_path(r'ws/chat/(?P<room_name>\w+)/$', VideoChatConsumer.as_asgi()),
]
