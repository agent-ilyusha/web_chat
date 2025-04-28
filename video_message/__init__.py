# import django.dispatch
#
# from video_message.views import on_shutdown_django
#
# app_shutdown_signal = django.dispatch.Signal()
#
#
# async def shutdown_handler(sender, **kwargs):
#     await on_shutdown_django(None, None, None)
#
#
# app_shutdown_signal.connect(shutdown_handler)