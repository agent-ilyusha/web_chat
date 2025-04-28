"""
URL configuration for vits project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path

from users_profile.views import (
    Registration,
    LoginUser,
    logout_view,
    profile,
    friends,
    home,
)
from chat.views import (
    chat,
    chat_list
)

from video_message.views import (
    view_offer
)

urlpatterns = [
    path('', home, name='home'),
    path('admin/', admin.site.urls),
    path('login/', LoginUser.as_view(), name='login'),
    path('registration/', Registration.as_view(), name='users'),
    path('logout/', logout_view, name='logout'),
    path('profile/', profile, name='profile'),
    path('friends/', friends, name='friends'),
    path('chats/', chat_list, name='chat_list'),
    path('chats/<str:room_name>/', chat, name='chat'),
    path('video_chat/', view_offer, name='offer_url'),
]
