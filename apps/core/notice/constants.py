# -*- coding: utf-8 -*-

from django.db.models import TextChoices
from django.utils.translation import gettext_lazy as _lazy


class NoticeWay(TextChoices):
    SMS = "sms", _lazy("短信")
    EMAIL = "email", _lazy("邮件")
    WEIXIN = "wechat", _lazy("微信")
    QY_WEIXIN = "wecom", _lazy("企业微信")
    VOICE = "voice", _lazy("电话")
    WX_BOT = "wecom_bot", _lazy("企业微信机器人")
