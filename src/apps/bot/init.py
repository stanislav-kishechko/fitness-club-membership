import telebot
from decouple import config

bot = telebot.TeleBot(config("TG_BOT_TOKEN"))
