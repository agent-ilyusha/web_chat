from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect

from users_profile.models import User
from users_profile.views import get_friends


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


def chat(request, room_name):
    if not request.user.is_authenticated:
        return redirect("/login/")
    usernames = room_name.split('_')

    other_username = usernames[0] if usernames[0] != request.user.username else usernames[1]
    try:
        other_user = User.objects.get(username=other_username)
    except User.DoesNotExist:
        return redirect("/chats/")

    # Получаем список всех чатов пользователя
    friends_usernames = get_friends(request.user.id)
    chats = []
    for username in friends_usernames:
        try:
            user = User.objects.get(username=username)
            chats.append({
                'id': f"{user.username}_{request.user.username}",
                'user_name': user.username,
                'last_message': ''
            })
        except User.DoesNotExist:
            continue

    context = {
        'room_name': room_name,
        'current_chat_user': other_user.username,
        'current_chat_id': room_name,
        'chats': chats
    }

    return render(request, 'users/chats/chat.html', context)
