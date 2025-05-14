# -- coding: utf-8
from multiprocessing.connection import Client
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from .models import User, UserToUser, InviteToFriend

User = get_user_model()


class UserModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            nickname='Test User',
            bio='Test bio'
        )

    def test_user_creation(self):
        self.assertEqual(self.user.username, 'testuser')
        self.assertEqual(self.user.nickname, 'Test User')
        self.assertEqual(self.user.bio, 'Test bio')
        self.assertTrue(isinstance(self.user, User))

    def test_user_str(self):
        self.assertEqual(str(self.user), self.user.username)


class UserToUserTest(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(
            username='user1',
            email='user1@example.com',
            password='testpass123',
            nickname='User 1'
        )
        self.user2 = User.objects.create_user(
            username='user2',
            email='user2@example.com',
            password='testpass123',
            nickname='User 2'
        )
        self.friendship = UserToUser.objects.create(
            user_first=self.user1,
            user_second=self.user2
        )

    def test_friendship_creation(self):
        self.assertEqual(self.friendship.user_first, self.user1)
        self.assertEqual(self.friendship.user_second, self.user2)
        self.assertTrue(isinstance(self.friendship, UserToUser))


class InviteToFriendTest(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(
            username='user1',
            email='user1@example.com',
            password='testpass123',
            nickname='User 1'
        )
        self.user2 = User.objects.create_user(
            username='user2',
            email='user2@example.com',
            password='testpass123',
            nickname='User 2'
        )
        self.invite = InviteToFriend.objects.create(
            user_first=self.user1,
            user_second=self.user2
        )

    def test_invite_creation(self):
        self.assertEqual(self.invite.user_first, self.user1)
        self.assertEqual(self.invite.user_second, self.user2)
        self.assertTrue(isinstance(self.invite, InviteToFriend))


class UserViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            nickname='Test User'
        )
        self.client.login(username='testuser', password='testpass123')

    def test_profile_view(self):
        response = self.client.get(reverse('profile'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'users/profile.html')
