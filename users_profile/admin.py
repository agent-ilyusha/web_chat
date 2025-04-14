# -- coding: utf-8

from django.contrib import admin

from users_profile.models import User
from users_profile.inline import UserToUserInline, InviteToFriendInline


class UserAdmin(admin.ModelAdmin):
    inlines = [UserToUserInline, InviteToFriendInline]


admin.site.register(User, UserAdmin)
