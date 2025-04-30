import asyncio
import json
import logging

from asgiref.sync import sync_to_async
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from aiortc import RTCPeerConnection, RTCSessionDescription
from aiortc.contrib.media import MediaRelay

logger = logging.getLogger(__name__)
pcs = set()
relay = MediaRelay()


@csrf_exempt
async def chat_room(request, room_name):
    if request.method == 'GET':
        context = {
            'chat_room_id': room_name,
        }
        val = await sync_to_async(render)(request,
                                          'users/video_chats/room.html',
                                          context,
                                          content_type='text/html',
                                          status=200,
                                          using=None)
        return val
    elif request.method == 'POST':
        val = await offer(request)
        return JsonResponse(val)


async def offer(request):
    params = json.loads(request.body)
    offer_val = RTCSessionDescription(sdp=params["sdp"], type=params["type"])

    pc = RTCPeerConnection()
    pcs.add(pc)

    @pc.on("connectionstatechange")
    async def on_connectionstatechange():
        if pc.connectionState == "failed":
            await pc.close()
            pcs.discard(pc)

    @pc.on("track")
    def on_track(track):
        if track.kind == "audio":
            pc.addTrack(relay.subscribe(track))
        elif track.kind == "video":
            pc.addTrack(relay.subscribe(track))

        @track.on("ended")
        async def on_ended():
            logger.info("Track %s ended", track.kind)

    # Устанавливаем удаленное описание
    await pc.setRemoteDescription(offer_val)

    # Создаем ответ
    answer = await pc.createAnswer()
    await pc.setLocalDescription(answer)

    return {
        "sdp": pc.localDescription.sdp,
        "type": pc.localDescription.type
    }


@csrf_exempt
async def close_room(request, room_name):
    # Закрываем все соединения
    coros = [pc.close() for pc in pcs]
    await asyncio.gather(*coros)
    pcs.clear()

    return HttpResponse("OK")
