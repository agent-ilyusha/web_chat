import json
import logging

from collections import defaultdict

from asgiref.sync import sync_to_async
from django.core.handlers.asgi import ASGIRequest
from django.http import JsonResponse, HttpResponseBadRequest, HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

logger = logging.getLogger(__name__)
rooms = defaultdict(dict)


@sync_to_async
def check_auth(request: ASGIRequest) -> bool:
    """
    Check authentication user.
    :param request:
    :return: boolean
    """
    return request.user.is_authenticated


@sync_to_async
def create_rooms(request: ASGIRequest, room_name: str) -> str:
    """
    Create room name.
    :param request:
    :param room_name:
    :return: room name
    """
    return f'{room_name}_{request.user.username}'


@sync_to_async
def async_render(request: ASGIRequest, context: dict, url: str) -> HttpResponse:
    return render(request, url, context)


@sync_to_async
def async_redirect(url: str) -> HttpResponseRedirect:
    return redirect(url)


@csrf_exempt
@require_http_methods(["POST", "GET"])
async def signaling(request: ASGIRequest, room_name):
    """
    Main view for video signaling.
    :param request:
    :param room_name:
    :return:
    """
    """
    Field in POST request.
    - room_id: room id.
    - role: 'offer' or 'answer'
    - sdp: SDP offer/answer (optional)
    - type: type SDP (optional)
    - candidate: ICE-candidate (optional)
    - sdpMid, sdpMLineIndex: for ICE-candidate (optional)
    """
    auth = await check_auth(request)
    if not auth:
        val = await async_redirect('/login/')
        return val

    room_true = await create_rooms(request, room_name)
    if request.method == 'GET':
        context = {
            'room_id': room_true,
        }
        val = await async_render(request,
                                 context,
                                 'users/video_chats/room.html')
        return val
    data = json.loads(request.body)
    room_id = data.get("room_id")
    role = data.get("role")

    if not room_id or role not in ("offer", "answer"):
        return HttpResponseBadRequest("room_id и role обязательны")

    room = rooms[room_id]
    if room_true != room:
        return HttpResponseBadRequest("Это не ваша комната!")

    if "candidate" in data:
        candidate = {
            "candidate": data["candidate"],
            "sdpMid": data.get("sdpMid"),
            "sdpMLineIndex": data.get("sdpMLineIndex"),
        }
        key = f"{role}_candidates"
        room.setdefault(key, []).append(candidate)
        return JsonResponse({"result": "candidate saved"})

    if "sdp" in data and "type" in data:
        sdp_obj = {
            "sdp": data["sdp"],
            "type": data["type"]
        }
        room[role] = sdp_obj
        return JsonResponse({"result": f"{role} saved"})

    if role == "offer":
        answer = room.get("answer")
        answer_candidates = room.get("answer_candidates", [])
        return JsonResponse({
            "answer": answer,
            "candidates": answer_candidates
        })
    else:
        offer = room.get("offer")
        offer_candidates = room.get("offer_candidates", [])
        return JsonResponse({
            "offer": offer,
            "candidates": offer_candidates
        })


@csrf_exempt
@require_http_methods(["POST"])
async def clear_room(request, room_name):
    """
    Clear room after close.
    :param request:
    :param room_name: room id
    :return:
    """
    data = json.loads(request.body)
    room_id = data.get("room_id")
    if room_id in rooms:
        del rooms[room_id]
    return JsonResponse({"result": "room cleared"})
