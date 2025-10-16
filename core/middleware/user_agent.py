from django.conf import settings

from xTool.constants import RE_MOBILE, RE_WECHAT


class UserAgentMiddleware:
    def process_request(self, request):
        request.is_mobile = lambda: bool(RE_MOBILE.search(request.META.get("HTTP_USER_AGENT", "")))

        request.is_rio = lambda: bool(
            request.META.get("HTTP_STAFFNAME", "")
            and getattr(settings, "RIO_TOKEN", None)
            and RE_WECHAT.search(request.META.get("HTTP_USER_AGENT", ""))
        )

        request.is_wechat = lambda: bool(
            RE_WECHAT.search(request.META.get("HTTP_USER_AGENT", "")) and not request.is_rio()
        )

        request.is_bk_jwt = lambda: bool(request.META.get("HTTP_X_BKAPI_JWT", ""))
