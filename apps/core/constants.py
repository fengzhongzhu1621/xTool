# -*- coding: utf-8 -*-

from enum import Enum

from django.db.models import TextChoices
from django.utils.translation import gettext_lazy as _lazy
from iam.contrib.http import HTTP_AUTH_FORBIDDEN_CODE


class NoticeWay(TextChoices):
    SMS = "sms", _lazy("短信")
    EMAIL = "email", _lazy("邮件")
    WECHAT = "wechat", _lazy("微信")
    WECOM = "wecom", _lazy("企业微信")
    VOICE = "voice", _lazy("电话")
    WECOM_BOT = "wecom_bot", _lazy("企业微信机器人")


class ErrorCode(Enum):
    IAM_NOT_PERMISSION = HTTP_AUTH_FORBIDDEN_CODE
