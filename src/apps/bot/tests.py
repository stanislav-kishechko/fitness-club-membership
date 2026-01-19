from decouple import config
from django.test import TestCase

from apps.bot.main import tg_bot


class TgBotTestCase(TestCase):
    def test_bot_can_send_message(self):
        text_sample = "Test notification"
        result = tg_bot.send_message(
            cid=config("TG_CHAT_ID"),
            text=text_sample
        )
        self.assertEqual(result.text, text_sample)
