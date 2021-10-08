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


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ControlString_co.settings')
os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"

app = Celery('tasks', broker=CELERY_BROKER_URL)

app.autodiscover_tasks()
CELERYD_CONCURRENCY = 1
CELERYD_PREFETCH_MULTIPLIER = 1
CELERY_ACKS_LATE = True



app.conf.beat_schedule = {
    # Execute the Speed Test every 10 minutes
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



