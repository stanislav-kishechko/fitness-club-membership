from django.db.models.signals import post_save
from django.dispatch import receiver

from apps.payments.models import Payment
from apps.payments.tasks import sent_pay_notification_to_admin_chat


@receiver(post_save, sender=Payment)
def post_payment_handler(sender, instance, created):
    #todo add salary
    sent_pay_notification_to_admin_chat(sender, instance, created)
