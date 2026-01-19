from decouple import config

from apps.bot.main import tg_bot


def send_telegram_notification(text):
    cid = config("TG_CHAT_ID")
    tg_bot.send_message(cid, text, parse_mode="HTML")
