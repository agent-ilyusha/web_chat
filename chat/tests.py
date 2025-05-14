import json
import os

from django.test import TestCase, Client, TransactionTestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from channels.testing import WebsocketCommunicator
from channels.layers import get_channel_layer
from channels.db import database_sync_to_async

from .consumers import ChatConsumer

User = get_user_model()


class ChatViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            nickname='Test User'
        )
        self.client.login(username='testuser', password='testpass123')

    def test_chat_room_view(self):
        response = self.client.get(reverse('chat', kwargs={'room_name': 'test-room'}), follow=True)
        self.assertEqual(response.status_code, 200)

    def test_chat_list_view(self):
        response = self.client.get(reverse('chat_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/chats/chat_list.html')


@database_sync_to_async
def create_user():
    return User.objects.create_user(
        username='testuser_consumer',
        email='test_consumer@example.com',
        password='testpass123',
        nickname='Test Consumer User'
    )


class ChatConsumerTest(TransactionTestCase):
    def setUp(self):
        self.channel_layer = get_channel_layer()
        
    async def test_chat_room_consumer(self):
        user = await create_user()

        communicator = WebsocketCommunicator(
            ChatConsumer.as_asgi(),
            "/ws/chat/test-room/"
        )

        communicator.scope["user"] = user

        communicator.scope["url_route"] = {"kwargs": {"room_name": "test-room"}}

        communicator.scope["channel_layer"] = self.channel_layer

        connected, _ = await communicator.connect()
        self.assertTrue(connected, "Не удалось установить WebSocket соединение")

        await communicator.send_json_to({
            'message': 'Тестовое сообщение',
            'username': user.username,
            'timestamp': '2023-10-20T12:00:00.000Z'
        })

        if os.path.exists('static/chats_data/test-room.json'):
            self.assertTrue(os.path.exists('static/chats_data/test-room.json'))
            os.remove('static/chats_data/test-room.json')
        else:
            assert False
