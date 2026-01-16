from decouple import config

from apps.bot.main import tg_bot


def sent_user_enroll_notification_to_admin_chat(instance, created):
    if created:
        first_name = instance.first_name
        last_name = instance.last_name
        full_name = f"{first_name} {last_name}"
        email = instance.email
        text = f"User enrolled\n\n" \
               f"👤 User: {full_name}\n" \
               f"📧 Email: {email}\n"
        cid = config("TG_CHAT_ID")
        tg_bot.send_message(cid, text, parse_mode="HTML")
