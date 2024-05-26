from django.conf import settings

from xTool.constants import RE_MOBILE, RE_WECHAT

__all__ = ["is_mobile", "is_rio"]


def is_mobile(request):
    """判断请求是否是从移动端发起的 ."""
    return bool(RE_MOBILE.search(request.META.get("HTTP_USER_AGENT", "")))


def is_rio(request):
    return bool(
        request.META.get("HTTP_STAFFNAME", "")
        and getattr(settings, "RIO_TOKEN", None)
        and RE_WECHAT.search(request.META.get("HTTP_USER_AGENT", ""))
    )
