# -- coding: utf-8
import uuid

from django.contrib.auth import logout
from django.contrib.auth.views import LoginView
from django.core.handlers.wsgi import WSGIRequest
from django.shortcuts import redirect, render
from django.views.generic import CreateView
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model

from users_profile.forms import RegistrationUserForm, LoginUserForm
from users_profile.models import UserToUser, User, InviteToFriend

from typing import Any


def get_friends(user_id: uuid, flag: str = 'friend') -> list[Any]:

    if flag == 'friend':
        users1 = UserToUser.objects.all().filter(user_first=user_id)
        users2 = UserToUser.objects.all().filter(user_second=user_id)
        users1 = {User.objects.get(username=user.user_first) for user in users1}.union(
            User.objects.get(username=user.user_second) for user in users1
        )
        users2 = {User.objects.get(username=user.user_second) for user in users2}.union(
            User.objects.get(username=user.user_first) for user in users2
        )

        list_friends = [user.username
                        for user in users1.union(users2) if user.id != user_id
                        ]
        return list_friends
    elif flag == 'output':
        list_your_invite = [User.objects.get(username=user.user_second).username
                            for user in InviteToFriend.objects.all().filter(user_first=user_id)
                            ]
        return list_your_invite
    elif flag == 'input':
        list_to_me_invite = [User.objects.get(username=user.user_first).username
                             for user in InviteToFriend.objects.all().filter(user_second=user_id)
                             ]
        return list_to_me_invite


def invite_to_friends(request: WSGIRequest):
    if not request.user.is_authenticated:
        return redirect("/login/")
    username = request.POST.get("user_id")
    if username == request.user.username:
        return redirect("/friends/")
    user = User.objects.get(username=username)
    take_id = InviteToFriend.objects.filter(user_first=user, user_second=request.user)
    if not take_id[0]:
        InviteToFriend.objects.create(user_first=request.user, user_second=user)
    return redirect("/friends/")


def apply_invite(request: WSGIRequest):
    if not request.user.is_authenticated:
        return redirect("/login/")
    user_id = request.POST.get("user_id")
    user = User.objects.get(username=user_id)
    if request.POST.get("apply") and request.POST.get("apply").lower() == "true":
        take_id = InviteToFriend.objects.filter(user_first=user, user_second=request.user)
        if take_id[0]:
            UserToUser.objects.create(user_first=request.user, user_second=user)
            InviteToFriend.objects.filter(id=take_id[0].id).delete()
    elif request.POST.get("apply") and request.POST.get("apply").lower() == "false":
        take_id = InviteToFriend.objects.filter(user_first=user, user_second=request.user)
        if take_id[0]:
            InviteToFriend.objects.filter(id=take_id[0].id).delete()
    return redirect("/friends/")


class Registration(CreateView):
    form_class = RegistrationUserForm
    template_name = "login/registration.html"
    success_url = "/login/"
    extra_context = {'title': "Регистрация"}

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('/profile/')
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return "/profile/"


class LoginUser(LoginView):
    form_class = LoginUserForm
    template_name = "login/login.html"
    extra_context = {'title': 'Авторизация'}

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('/profile/')
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return "/profile/"


def logout_view(request: WSGIRequest):
    logout(request)
    return redirect("/login/")


def profile(request: WSGIRequest):
    if not request.user.is_authenticated:
        return redirect("/login/")
    list_friends = get_friends(request.user.id)
    return render(
        request,
        "users/profile.html",
        {
            "name": request.user.nickname,
            "login_name": request.user.username,
            "friends": list_friends[:5],
        },
    )


def friends(request: WSGIRequest):
    if not request.user.is_authenticated:
        return redirect("/login/")
    if request.method == "POST" and request.POST.get('name_but') == 'input':
        return render(
            request,
            "users/friends/friends_invite_inp.html",
            {
                "list_to_me_invite": get_friends(request.user.id, 'input')
            }
        )
    elif request.method == "POST" and request.POST.get('name_but') == 'output':
        return render(
            request,
            "users/friends/friends_invite_out.html",
            {
                "list_your_invite": get_friends(request.user.id, 'output'),
            }
        )
    elif request.method == "POST" and request.POST.get('apply') and request.POST.get('user_id'):
        apply_invite(request)
    elif request.method == "POST" and request.POST.get('user_id'):
        invite_to_friends(request)
    return render(
        request,
        "users/friends/friends.html",
        {
            "list_friends": get_friends(request.user.id),
        }
    )


@login_required
def chat_list(request):
    if not request.user.is_authenticated:
        return redirect("/login/")
        
    friends_usernames = get_friends(request.user.id)
    
    users = []
    for username in friends_usernames:
        try:
            user = User.objects.get(username=username)
            users.append(user)
        except User.DoesNotExist:
            continue
    
    context = {
        'users': users
    }
    return render(request, 'users/chats/chat_list.html', context)


@login_required
def chat(request, room_name):
    if not request.user.is_authenticated:
        return redirect("/login/")
        
    usernames = room_name.split('_')
        
    other_username = usernames[0] if usernames[0] != request.user.username else usernames[1]
    try:
        other_user = User.objects.get(username=other_username)
    except User.DoesNotExist:
        return redirect("/chats/")

    context = {
        'room_name': room_name,
        'current_chat_user': other_user.username,
        'current_chat_id': room_name
    }
    
    return render(request, 'users/chats.html', context)


@login_required
def home(request):
    return render(request, 'home.html')
