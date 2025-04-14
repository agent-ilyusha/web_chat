# -- coding: utf-8
import uuid

from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _

from users_profile.constant import MAX_LENGTH_USER_NAME, MAX_LENGTH_USER_BIO


class User(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    username = models.CharField(_('username'), max_length=MAX_LENGTH_USER_NAME, blank=False, null=False, unique=True)
    nickname = models.CharField(_('nickname'), max_length=MAX_LENGTH_USER_NAME, blank=False, null=False, unique=False)
    bio = models.TextField(_('bio'), max_length=MAX_LENGTH_USER_BIO, blank=True, null=True)
    birth_date = models.DateField(_('birth_date'), null=True, blank=True)
    friends = models.ManyToManyField('User',
                                     through='UserToUser',
                                     verbose_name=_('friends'),
                                     related_name='user_friends')


class AbstractModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user_first = models.ForeignKey('User',
                                   on_delete=models.CASCADE,
                                   related_name='user_first',
                                   verbose_name=_('user_first'))
    user_second = models.ForeignKey('User',
                                    on_delete=models.CASCADE,
                                    related_name='user_second',
                                    verbose_name=_('user_second'))


class UserToUser(AbstractModel):
    class Meta:
        verbose_name = _('UserToUser')
        verbose_name_plural = _('UsersToUsers')


class InviteToFriend(AbstractModel):
    class Meta:
        verbose_name = _('InviteToFriend')
        verbose_name_plural = _('InviteToFriends')
