from django.db.models.signals import post_save
from django.dispatch import receiver

from apps.user.models import User
from apps.user.tasks import sent_user_enroll_notification_to_admin_chat


@receiver(post_save, sender=User)
def post_user_handler(sender, instance, created, **kwargs):  # noqa
    # TODO: add salary
    sent_user_enroll_notification_to_admin_chat(instance, created)
