# -- coding: utf-8

from django.contrib import admin
from users_profile.models import UserToUser, InviteToFriend


class UserToUserInline(admin.TabularInline):
    model = UserToUser
    fk_name = 'user_first'
    extra = 1


class InviteToFriendInline(admin.TabularInline):
    model = InviteToFriend
    fk_name = 'user_first'
    extra = 1
