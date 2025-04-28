import asyncio
import json
import os
import uuid

import cv2

from aiortc import RTCPeerConnection, RTCSessionDescription, MediaStreamTrack
from aiortc.contrib.media import MediaPlayer, MediaRelay, MediaBlackhole
from av import VideoFrame

from django.core.handlers.wsgi import WSGIRequest
from django.core.handlers.asgi import ASGIRequest
from django.core.asgi import get_asgi_application
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt

from users_profile.models import User
from video_message.constant import FACES, EYES, pcs


# class VideoTransformTrack(MediaStreamTrack):
#     """
#     A video stream track that transforms frames from an another track.
#     """
#
#     kind = "audio"
#
#     def __init__(self, track, transform):
#         super().__init__()
#         self.track = track
#         self.transform = transform
#
#     async def recv(self):
#         frame = await self.track.recv()
#
#         if self.transform == "cartoon":
#             img = frame.to_ndarray(format="bgr24")
#
#             # prepare color
#             img_color = cv2.pyrDown(cv2.pyrDown(img))
#             for _ in range(6):
#                 img_color = cv2.bilateralFilter(img_color, 9, 9, 7)
#             img_color = cv2.pyrUp(cv2.pyrUp(img_color))
#
#             # prepare edges
#             img_edges = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
#             img_edges = cv2.adaptiveThreshold(
#                 cv2.medianBlur(img_edges, 7),
#                 255,
#                 cv2.ADAPTIVE_THRESH_MEAN_C,
#                 cv2.THRESH_BINARY,
#                 9,
#                 2,
#             )
#             img_edges = cv2.cvtColor(img_edges, cv2.COLOR_GRAY2RGB)
#
#             # combine color and edges
#             img = cv2.bitwise_and(img_color, img_edges)
#
#             # rebuild a VideoFrame, preserving timing information
#             new_frame = VideoFrame.from_ndarray(img, format="bgr24")
#             new_frame.pts = frame.pts
#             new_frame.time_base = frame.time_base
#             return new_frame
#         elif self.transform == "edges":
#             # perform edge detection
#             img = frame.to_ndarray(format="bgr24")
#             img = cv2.cvtColor(cv2.Canny(img, 100, 200), cv2.COLOR_GRAY2BGR)
#
#             # rebuild a VideoFrame, preserving timing information
#             new_frame = VideoFrame.from_ndarray(img, format="bgr24")
#             new_frame.pts = frame.pts
#             new_frame.time_base = frame.time_base
#             return new_frame
#         elif self.transform == "rotate":
#             # rotate image
#             img = frame.to_ndarray(format="bgr24")
#             rows, cols, _ = img.shape
#             M = cv2.getRotationMatrix2D((cols / 2, rows / 2), frame.time * 45, 1)
#             img = cv2.warpAffine(img, M, (cols, rows))
#
#             # rebuild a VideoFrame, preserving timing information
#             new_frame = VideoFrame.from_ndarray(img, format="bgr24")
#             new_frame.pts = frame.pts
#             new_frame.time_base = frame.time_base
#             return new_frame
#         elif self.transform == "cv":
#             img = frame.to_ndarray(format="bgr24")
#             face = FACES.detectMultiScale(img, 1.1, 19)
#             for (x, y, w, h) in face:
#                 cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)
#
#             eye = EYES.detectMultiScale(img, 1.1, 19)
#             for (x, y, w, h) in eye:
#                 cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)
#
#             new_frame = VideoFrame.from_ndarray(img, format="bgr24")
#             new_frame.pts = frame.pts
#             new_frame.time_base = frame.time_base
#             return new_frame
#         else:
#             return frame
#
#
# def create_local_tracks(play_from=None):
#     if play_from:
#         player = MediaPlayer(play_from)
#         return player.audio, player.video
#     else:
#         options = {"framerate": "30", "video_size": "1920x1080"}
#         webcam = MediaPlayer(
#             "video=FULL HD 1080P Webcam", format="dshow", options=options
#         )
#         relay = MediaRelay()
#         return None, relay.subscribe(webcam.video)


@csrf_exempt
def view_offer(request: ASGIRequest, room_name='mandarinka'):
    if request.method == 'GET':
        try:
            other_user = User.objects.get(username=room_name)
        except User.DoesNotExist:
            return redirect('/chats/')
        context = {
            'room_name': room_name,
            'current_chat_user': other_user.username,
            'current_chat_id': room_name,
        }
        return render(request, 'users/video_chats/video_chat.html', context)
    elif request.method == 'POST':
        data = json.loads(request.body.decode('utf-8'))
        val = asyncio.run(offer(data))
        return JsonResponse(
            val,
        )
    else:
        return redirect('/chats/')


@csrf_exempt
async def offer(request):
    try:
        params = request
        offer_var = RTCSessionDescription(sdp=params["sdp"], type=params["type"])

        pc = RTCPeerConnection()
        pcs.add(pc)

        # подготовка локального медиа
        recorder = MediaBlackhole()


        @pc.on("datachannel")
        def on_datachannel(channel):
            @channel.on("message")
            def on_message(message):
                if isinstance(message, str) and message.startswith("ping"):
                    channel.send("pong" + message[4:])


        @pc.on("iceconnectionstatechange")
        async def on_iceconnectionstatechange():
            if pc.iceConnectionState == "failed":
                await pc.close()
                pcs.discard(pc)


        # @pc.on("track")
        # def on_track(track):
        #     if track.kind == "audio":
        #         pc.addTrack(player.audio)
        #         recorder.addTrack(track)
        #     elif track.kind == "video":
        #         video_transform = params.get("video_transform")
        #         if video_transform:
        #             local_video = VideoTransformTrack(
        #                 track, transform=video_transform
        #             )
        #             pc.addTrack(local_video)

        # @track.on("ended")
        # async def on_ended():
        #     await recorder.stop()

        # обработка offer
        await pc.setRemoteDescription(offer_var)
        await recorder.start()

        # отправка answer
        answer = await pc.createAnswer()
        await pc.setLocalDescription(answer)

        return {"sdp": pc.localDescription.sdp, "type": pc.localDescription.type}

    except json.JSONDecodeError:
        return JsonResponse({"error": "Некорректный JSON"}, status=400)
    except KeyError as e:
        return JsonResponse({"error": f"Отсутствует ключ: {e}"}, status=400)
    except Exception as e:
        return JsonResponse({"error": "Внутренняя ошибка сервера:"}, status=500)


async def on_shutdown_django(signal, sender, app, **kwargs):
    coros = [pc.close() for pc in pcs]
    await asyncio.gather(*coros)
    pcs.clear()
