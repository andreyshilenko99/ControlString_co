"""
Файл настроек Celery
https://docs.celeryproject.org/en/stable/django/first-steps-with-django.html
"""
from __future__ import absolute_import
import os
from celery import Celery

from ControlString_co.trace import trace

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ControlString_co.settings')
os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"

# здесь вы меняете имя
app = Celery('tasks', broker='redis://127.0.0.1:6379')

app.autodiscover_tasks()


@app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    sender.add_periodic_task(3, trace_host.s('192.168.2.241'), name='host1')
    sender.add_periodic_task(3, trace_host.s('192.168.2.242'), name='host2')


@app.task
def trace_host(host):
    trace(host)
