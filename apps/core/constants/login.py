from django.db.models import TextChoices
from django.utils.translation import gettext_lazy as _lazy


class LoginType(TextChoices):
    """用户登录方式 ."""

    NORMAL = "NORMAL", _lazy("普通登录")
    WECHAT_SCAN_CODE = "WECHAT_SCAN_CODE", _lazy("微信扫码登录")
