import datetime
import time
from typing import Dict

from django.http import parse_cookie
from django.http.cookie import SimpleCookie
from django.utils import timezone
from django.utils.encoding import force_str
from django.utils.http import http_date


class CookieMiddlewareDecorator:
    """
    Extracts cookies from HTTP or WebSocket-style scopes and adds them as a
    scope["cookies"] entry with the same format as Django's request.COOKIES.
    """

    def __init__(self, inner):
        self.inner = inner

    # async def __call__(self, *args, **kwargs) 是一个异步特殊方法，用于定义一个异步可调用对象。
    # 当你将一个对象作为协程调用时（即使用 await 关键字），Python 会自动调用对象的 __call__ 方法。这使得你可以将类的实例用作异步函数。
    async def __call__(self, scope, receive, send):
        """定义一个异步装饰器 ."""
        # Check this actually has headers. They're a required scope key for HTTP and WS.
        if "headers" not in scope:
            raise ValueError(
                "CookieMiddleware was passed a scope that did not have a headers key "
                + "(make sure it is only passed HTTP or WebSocket connections)"
            )
        # 从请求头中获取 cookie 的值
        # Go through headers to find the cookie one
        for name, value in scope.get("headers", []):
            if name == b"cookie":
                cookies = parse_cookie(value.decode("latin1"))
                break
        else:
            # No cookie header found - add an empty default.
            cookies = {}
        # Return inner application
        # 在 scope 中添加 cookies
        return await self.inner(dict(scope, cookies=cookies), receive, send)

    @classmethod
    def set_cookie(
        cls,
        message: Dict,
        key,
        value="",
        max_age=None,
        expires=None,
        path="/",
        domain=None,
        secure=False,
        httponly=False,
        samesite="lax",
    ):
        """
        Sets a cookie in the passed HTTP response message.

        ``expires`` can be:
        - a string in the correct format,
        - a naive ``datetime.datetime`` object in UTC,
        - an aware ``datetime.datetime`` object in any time zone.
        If it is a ``datetime.datetime`` object then ``max_age`` will be calculated.
        """
        value = force_str(value)
        cookies = SimpleCookie()
        cookies[key] = value
        if expires is not None:
            if isinstance(expires, datetime.datetime):
                if timezone.is_aware(expires):
                    expires = timezone.make_naive(expires, timezone.utc)
                delta = expires - expires.utcnow()
                # Add one second so the date matches exactly (a fraction of
                # time gets lost between converting to a timedelta and
                # then the date string).
                delta = delta + datetime.timedelta(seconds=1)
                # Just set max_age - the max_age logic will set expires.
                expires = None
                max_age = max(0, delta.days * 86400 + delta.seconds)
            else:
                cookies[key]["expires"] = expires
        else:
            cookies[key]["expires"] = ""
        if max_age is not None:
            cookies[key]["max-age"] = max_age
            # IE requires expires, so set it if hasn't been already.
            if not expires:
                cookies[key]["expires"] = http_date(time.time() + max_age)
        if path is not None:
            cookies[key]["path"] = path
        if domain is not None:
            cookies[key]["domain"] = domain
        if secure:
            cookies[key]["secure"] = True
        if httponly:
            cookies[key]["httponly"] = True
        if samesite is not None:
            assert samesite.lower() in [
                "strict",
                "lax",
                "none",
            ], "samesite must be either 'strict', 'lax' or 'none'"
            cookies[key]["samesite"] = samesite
        # Write out the cookies to the response
        for c in cookies.values():
            message.setdefault("headers", []).append(
                (b"Set-Cookie", bytes(c.output(header="").strip(), encoding="utf-8"))
            )

    @classmethod
    def delete_cookie(cls, message, key, path="/", domain=None):
        """
        Deletes a cookie in a response.
        """
        return cls.set_cookie(
            message,
            key,
            max_age=0,
            path=path,
            domain=domain,
            expires="Thu, 01-Jan-1970 00:00:00 GMT",
        )
