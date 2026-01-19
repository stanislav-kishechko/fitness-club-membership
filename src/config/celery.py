import os

from celery import Celery
from celery.schedules import crontab

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

app = Celery("config")

app.config_from_object("django.conf:settings", namespace="CELERY")

app.autodiscover_tasks()

app.conf.beat_schedule = {
    "mark-expired-memberships": {
        "task": "apps.memberships.tasks.mark_expired_memberships",
        "schedule": crontab(hour=0, minute=0),
    },

    "send-expiration-reminders-7-days": {
        "task": "apps.memberships.tasks.send_expiration_reminders",
        "schedule": crontab(hour=9, minute=0),
        "kwargs": {"days_before": 7},
    },

    "auto-renew-memberships": {
        "task": "apps.memberships.tasks.auto_renew_memberships",
        "schedule": crontab(hour=1, minute=0),
    },

    "expire-old-stripe-sessions": {
        "task": "apps.payments.tasks.expire_old_stripe_sessions",
        "schedule": crontab(hour=2, minute=0),
    },
}
