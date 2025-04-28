import json
import os

from channels.generic.websocket import AsyncWebsocketConsumer
from django.contrib.auth import get_user_model


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'vits.settings')


class VideoChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        """
        Call when client connects to websocket.
        :return:
        """
        print(1)
        self.User = get_user_model()

        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f'chat_{self.room_name}'

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()
        await self.send(text_data=json.dumps({
            'type': 'chat_history',
        }))

    async def disconnect(self, close_code):
        """
        Call when client disconnects from websocket.
        :param close_code:
        :return:
        """
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
