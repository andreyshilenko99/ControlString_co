"""
Файл настроек Celery
https://docs.celeryproject.org/en/stable/django/first-steps-with-django.html
"""
from __future__ import absolute_import
import os
from datetime import timedelta
from ControlString_co.settings import CELERY_BROKER_URL
from celery import Celery
from celery.schedules import crontab
from celery import shared_task
from ControlString_co.trace import trace
from ControlString_co.check_uniping import main_check
from ControlString_co.skyPoint import skypoint
from ControlString_co.check_strig import check_strig
from kombu import Exchange, Queue

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ControlString_co.settings')
os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"

app = Celery('tasks', broker=CELERY_BROKER_URL)

app.autodiscover_tasks()
# CELERYD_CONCURRENCY = 1
# CELERYD_PREFETCH_MULTIPLIER = 1
# CELERY_TACKS_LATE = False
app.control.purge()
app.conf.task_queues = (
    # Queue("default", Exchange("default"), routing_key="default"),
    Queue("for_check", Exchange("for_check"), routing_key="task_a"),
    Queue("for_info", Exchange("for_info"), routing_key="task_b"),
    Queue("for_aero", Exchange("for_aero"), routing_key="task_c")
)
app.conf.task_routes = {
    'check': {'queue': 'for_check', 'routing_key': 'task_a'},
    'get_info_trace': {'queue': 'for_info', 'routing_key': 'task_b'},
    'aeroScope': {'queue': 'for_aero', 'routing_key': 'task_c'},
}

app.conf.beat_schedule = {
    'get_info': {
        'task': 'get_info_trace',
        'schedule': timedelta(seconds=1),
    },
    'check_state': {
        'task': 'check',
        'schedule': timedelta(seconds=1),
    },
    'aeroScope': {
        'task': 'aeroScope',
        'schedule': timedelta(seconds=1),
    },
}


@shared_task(name='get_info_trace')
def get_info_trace():
    trace()


@shared_task(name='check')
def check():
    check_strig()


@shared_task(name='aeroScope')
def aeroScope():
    skypoint()
