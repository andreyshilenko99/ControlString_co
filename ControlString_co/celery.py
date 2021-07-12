"""
Файл настроек Celery
https://docs.celeryproject.org/en/stable/django/first-steps-with-django.html
"""
from __future__ import absolute_import
import os
import socket
from celery import Celery
import control_trace
from Trace import trace_remote_pb2 as con

# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ControlString_co.settings')

# здесь вы меняете имя
app = Celery('tasks', broker='redis://127.0.0.1:6379')


# Для получения настроек Django, связываем префикс "CELERY" с настройкой celery
# app.config_from_object('django.conf:settings', namespace='CELERY')
#
# # загрузка tasks.py в приложение django
# app.autodiscover_tasks()

@app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    # Calls test('hello') every 10 seconds.
    sender.add_periodic_task(3, test.s('192.168.2.241'), name='add every 10')


# app.conf.beat_schedule = {
#     'add-every-30-seconds': {
#         'task': 'tasks.test',
#         'schedule': 3.0,
#         'args': ('192.168.2.241',),
#     },
# }
# app.conf.timezone = 'UTC'


@app.task
def test(host):
    message = con.TraceRemoteMessage()
    message.message_type = 0

    lel = message.SerializeToString()
    print(message)

    port = 10100  # The same port as used by the server
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((host, port))
    s.send(bytearray(lel))
    s.close()
    print('dwk')
