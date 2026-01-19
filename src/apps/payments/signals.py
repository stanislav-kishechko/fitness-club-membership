from django.dispatch import Signal, receiver

from apps.payments.tasks import sent_pay_notification_to_admin_chat

payment_successful_signal = Signal()


@receiver(payment_successful_signal)
def post_payment_handler(sender, instance, **kwargs):  # noqa
    sent_pay_notification_to_admin_chat.delay(sender, instance)
