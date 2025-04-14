import json
import os
from channels.generic.websocket import AsyncWebsocketConsumer
from django.contrib.auth import get_user_model
from pathlib import Path


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'vits.settings')


class ChatConsumer(AsyncWebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.chats_dir = Path('static/chats_data')
        self.chats_dir.mkdir(exist_ok=True)

    def get_chat_file_path(self, room_name):
        usernames = room_name.split('_')
        sorted_usernames = sorted(usernames)
        filename = '_'.join(sorted_usernames) + '.json'
        return self.chats_dir / filename

    def load_chat_history(self, room_name):
        file_path = self.get_chat_file_path(room_name)
        if file_path.exists():
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []

    def save_message(self, room_name, message_data):
        file_path = self.get_chat_file_path(room_name)
        messages = self.load_chat_history(room_name)
        messages.append(message_data)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(messages, f, ensure_ascii=False, indent=2)

    async def connect(self):
        self.User = get_user_model()
        
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f'chat_{self.room_name}'

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

        chat_history = self.load_chat_history(self.room_name)
        await self.send(text_data=json.dumps({
            'type': 'chat_history',
            'messages': chat_history
        }))

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data=None, bytes_data=None):
        if text_data is None:
            return
            
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        username = text_data_json['username']
        timestamp = text_data_json.get('timestamp', '')

        message_data = {
            'message': message,
            'username': username,
            'timestamp': timestamp
        }

        self.save_message(self.room_name, message_data)

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'username': username,
                'timestamp': timestamp
            }
        )

    async def chat_message(self, event):
        message = event['message']
        username = event['username']
        timestamp = event['timestamp']

        await self.send(text_data=json.dumps({
            'message': message,
            'username': username,
            'timestamp': timestamp
        }))
