from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "library_service.settings")

app = Celery("library_service")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()
app.conf.broker_connection_retry_on_startup = True
app.conf.beat_schedule = {
    "check-overdue-borrowings-daily-at-nine": {
        "task": "borrowings.tasks.check_overdue_borrowings",
        "schedule": crontab(hour=22, minute=5),
    },
}
