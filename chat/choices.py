from django.db import models
from django.utils.translation import gettext_lazy as _


class MassageTypeChoices(models.IntegerChoices):
    TEXT_MESSAGE = (1, _("text"))
    FILE_MESSAGE = (2, _("image"))
    STICKER_MESSAGE = (3, _("sticker"))
    GIPHY_MESSAGE = (4, _("giphy"))


class MassageConnectionChoices(models.TextChoices):
    TYPE_MESSAGE = "chat_message"
    TYPE_JOIN = "chat_join"
    TYPE_RECONNECT = "chat_reconnect"
    TYPE_LEAVE = "chat_leave"
