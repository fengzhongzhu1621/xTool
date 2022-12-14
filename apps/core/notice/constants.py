# -*- coding: utf-8 -*-

from django.db.models import TextChoices
from django.utils.translation import gettext_lazy as _lazy


class NoticeWay(TextChoices):
    SMS = "sms", _lazy("短信")
    EMAIL = "email", _lazy("邮件")
    WECHAT = "wechat", _lazy("微信")
    WECOM = "wecom", _lazy("企业微信")
    VOICE = "voice", _lazy("电话")
    WECOM_BOT = "wecom_bot", _lazy("企业微信机器人")
