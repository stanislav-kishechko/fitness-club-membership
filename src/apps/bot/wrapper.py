from apps.bot.mixins import SubscriptionMixin, UnsubscriptionMixin

COMMANDS = {
    "start": "Get used to the bot",
    "help": "Gives you information about the available commands",
    "subscribe": "Subscribe fitness club notifications",
    "unsubscribe": "Unsubscribe fitness club notificatiions",
}


class BaseBotWrapper:
    def __init__(self, bot):
        self.bot = bot
        self.register_handlers()

    def register_handlers(self):
        @self.bot.message_handler(commands=["start"])
        def command_start(mes):  # noqa
            pass

    def run(self):
        self.bot.infinity_polling()

    def send_message(self, cid: int | str, text: str, **kwargs):
        self.bot.send_message(cid, text, **kwargs)


class SubscrUnsubscrBotWrapper(SubscriptionMixin, UnsubscriptionMixin, BaseBotWrapper):
    def register_handlers(self):
        super().register_handlers()

        @self.bot.message_handler(commands=["help"])
        def command_help(mes):
            cid = mes.chat.id
            help_text = "The following options are available: \n"
            for key in COMMANDS:
                help_text += "/" + key + ": "
                help_text += COMMANDS[key] + "\n"
            self.bot.send_message(cid, help_text)

        @self.bot.message_handler(commands=["subscribe"])
        def command_subscribe(mes):
            cid = mes.chat.id
            uid = mes.from_user.id
            self.subscribe(uid, cid)

        @self.bot.message_handler(commands=["unsubscribe"])
        def command_unsubscribe(mes):
            cid = mes.chat.id
            uid = mes.from_user.id
            self.unsubscribe(uid, cid)

        @self.bot.message_handler(func=lambda _: True)
        def command_default(mes):
            command_help(mes)
