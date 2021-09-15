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

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ControlString_co.settings')
os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"

app = Celery('tasks', broker=CELERY_BROKER_URL)

app.autodiscover_tasks()
CELERYD_CONCURRENCY = 1
CELERYD_PREFETCH_MULTIPLIER = 1
CELERY_ACKS_LATE = True

# @app.on_after_configure.connect
# def setup_periodic_tasks(sender, **kwargs):
#     # import celery.bin.amqp
#     # amqp = celery.bin.amqp.amqp(app=app)
#     # amqp.run('queue.purge', 'name_of_your_queue')
#     sender.add_periodic_task(3, trace_host, name='host1')
#     sender.add_periodic_task(3, trace_host, name='host2')
#     sender.add_periodic_task(10, uniping_info, name='uniping')


app.conf.beat_schedule = {
    # Execute the Speed Test every 10 minutes
    'get_info': {
        'task': 'get_info_trace',
        'schedule': timedelta(seconds=1),
    },
    'uniping': {
        'task': 'uniping',
        'schedule': crontab(minute='*/1'),
    },
}


@shared_task(name='get_info_trace')
def get_info_trace():
    trace()


@shared_task(name='uniping')
def uniping():
    main_check()

# @app.task
# def uniping_info():
#     main_check()
#
#
# @app.task
# def trace_host():
#     trace()


