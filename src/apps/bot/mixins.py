# todo: add user model
class User:
    def __init__(self, uid: int):
        self.uid = uid

    def exists(self) -> bool:
        return True

    def subscribed(self) -> bool:
        return True


class SubscriptionMixin:
    def subscribe(self, uid, cid):
        text_success = (
            "Success! You'll receive notifications about: \n"
            "new membership\n"
            "frozen membership\n"
            "success payments\n"
        )
        self.bot.send_message(cid, text_success)
        text_already_subscribed = "You're already subscribed!"
        text_not_registered = "You're not registered yet!"
        usr = User(uid)
        if usr.exists():
            if usr.subscribed is not None:
                self.bot.send_message(cid, text_already_subscribed)
                return
            usr.subscribed = cid
            usr.save()
            self.bot.send_message(cid, text_success)
            return
        self.bot.send_message(cid, text_not_registered)


class UnsubscriptionMixin:
    def unsubscribe(self, uid, cid):
        text_success = "You've succesfully unsubscribed"
        text_already_unsubscribed = "You're already unsubscribed!"
        text_not_registered = "You're not registered yet!"
        usr = User(uid)
        if usr.exists():
            if usr.subscribed is None:
                self.bot.send_message(cid, text_already_unsubscribed)
                return
            usr.subscribed = None
            usr.save()
            self.bot.send_message(cid, text_success)
            return
        self.bot.send_message(cid, text_not_registered)
