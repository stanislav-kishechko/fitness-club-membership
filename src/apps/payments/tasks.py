from celery import shared_task
from decouple import config

from apps.bot.main import tg_bot


@shared_task()
def sent_pay_notification_to_admin_chat(sender, instance):
    if instance.status == sender.StatusChoices.PAID:
        first_name = instance.user.first_name
        last_name = instance.user.last_name
        email = instance.user.email
        amount = instance.money_to_pay
        date = instance.created_at

        text = (
            f"💰 Payment Received\n\n"
            f"👤 First name: {first_name}\n"
            f"👤 Last name: {last_name}\n"
            f"📧 Email: {email}\n"
            f"💵 Amount: {amount}\n"
            f"📅 Date: {date}\n"
            f"🆔 Payment ID: {instance.id}"
        )
        cid = config("TG_CHAT_ID")
        tg_bot.send_message(cid, text, parse_mode="HTML")
