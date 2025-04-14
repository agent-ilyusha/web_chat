# -- coding: utf-8
from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.utils.translation import gettext_lazy as _


class RegistrationUserForm(UserCreationForm):
    username = forms.CharField(
        label=_('Логин пользователя'),
        widget=forms.TextInput(attrs={'class': 'form-input', 'id': 'id_username'}),
        max_length=35
    )
    nickname = forms.CharField(
        label=_('Ник пользователя'),
        widget=forms.TextInput(attrs={'class': 'form-input', 'id': 'id_nickname'}),
        max_length=35
    )
    password1 = forms.CharField(
        label=_('Пароль'),
        widget=forms.PasswordInput(attrs={'class': 'form-input', 'id': 'id_password1'}),
        max_length=40
    )
    password2 = forms.CharField(
        label=_('Подтверждение пароля'),
        widget=forms.PasswordInput(attrs={'class': 'form-input', 'id': 'id_password2'}),
        max_length=40
    )

    class Meta:
        model = get_user_model()
        fields = ('username', 'nickname', 'password1', 'password2')


class LoginUserForm(AuthenticationForm):
    username = forms.CharField(
        label=_('Логин'),
        widget=forms.TextInput(attrs={'class': 'form-input'})
    )
    password = forms.CharField(
        label=_('Пароль'),
        widget=forms.PasswordInput(attrs={'class': 'form-input'})
    )

    class Meta:
        model = get_user_model()
        fields = ('username', 'password')
