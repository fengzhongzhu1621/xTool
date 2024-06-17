import time
from importlib import import_module

from channels.db import database_sync_to_async
from django.conf import settings
from django.contrib.sessions.backends.base import UpdateError
from django.core.exceptions import SuspiciousOperation
from django.utils.functional import LazyObject
from django.utils.http import http_date

from .cookie import CookieMiddlewareDecorator


class InstanceSessionWrapper:
    """
    Populates the session in application instance scope, and wraps send to save
    the session.
    """

    # Message types that trigger a session save if it's modified
    save_message_types = ["http.response.start"]

    # Message types that can carry session cookies back
    cookie_response_message_types = ["http.response.start"]

    def __init__(self, scope, send):
        self.cookie_name = settings.SESSION_COOKIE_NAME
        self.session_store = import_module(settings.SESSION_ENGINE).SessionStore

        self.scope = dict(scope)

        if "session" in self.scope:
            # There's already session middleware of some kind above us, pass
            # that through
            self.activated = False
        else:
            # Make sure there are cookies in the scope
            if "cookies" not in self.scope:
                raise ValueError("No cookies in scope - SessionMiddleware needs to run " "inside of CookieMiddleware.")
            # Parse the headers in the scope into cookies
            self.scope["session"] = LazyObject()  # 创建一个懒加载对象，值在resolve_session 中设置
            self.activated = True

        # Override send
        self.real_send = send

    async def resolve_session(self):
        # 从 cookie 中获得 session_key
        session_key = self.scope["cookies"].get(self.cookie_name)
        # 根据 session_key 获取 session 的值，设置懒加载对象的值
        self.scope["session"]._wrapped = await database_sync_to_async(self.session_store)(session_key)

    async def send(self, message):
        """
        Overridden send that also does session saves/cookies.
        """
        # Only save session if we're the outermost session middleware
        if self.activated:
            modified = self.scope["session"].modified
            empty = self.scope["session"].is_empty()
            # If this is a message type that we want to save on, and there's
            # changed data, save it. We also save if it's empty as we might
            # not be able to send a cookie-delete along with this message.
            if (
                message["type"] in self.save_message_types
                and message.get("status", 200) != 500
                and (modified or settings.SESSION_SAVE_EVERY_REQUEST)
            ):
                await database_sync_to_async(self.save_session)()
                # If this is a message type that can transport cookies back to the
                # client, then do so.
                if message["type"] in self.cookie_response_message_types:
                    if empty:
                        # Delete cookie if it's set
                        if settings.SESSION_COOKIE_NAME in self.scope["cookies"]:
                            CookieMiddlewareDecorator.delete_cookie(
                                message,
                                settings.SESSION_COOKIE_NAME,
                                path=settings.SESSION_COOKIE_PATH,
                                domain=settings.SESSION_COOKIE_DOMAIN,
                            )
                    else:
                        # Get the expiry data
                        if self.scope["session"].get_expire_at_browser_close():
                            max_age = None
                            expires = None
                        else:
                            max_age = self.scope["session"].get_expiry_age()
                            expires_time = time.time() + max_age
                            expires = http_date(expires_time)
                        # Set the cookie
                        CookieMiddlewareDecorator.set_cookie(
                            message,
                            self.cookie_name,
                            self.scope["session"].session_key,
                            max_age=max_age,
                            expires=expires,
                            domain=settings.SESSION_COOKIE_DOMAIN,
                            path=settings.SESSION_COOKIE_PATH,
                            secure=settings.SESSION_COOKIE_SECURE or None,
                            httponly=settings.SESSION_COOKIE_HTTPONLY or None,
                            samesite=settings.SESSION_COOKIE_SAMESITE,
                        )
        # Pass up the send
        return await self.real_send(message)

    def save_session(self):
        """
        Saves the current session.
        """
        try:
            self.scope["session"].save()
        except UpdateError:
            raise SuspiciousOperation(
                "The request's session was deleted before the "
                "request completed. The user may have logged "
                "out in a concurrent request, for example."
            )


class SessionMiddlewareDecorator:
    """
    Class that adds Django sessions (from HTTP cookies) to the
    scope. Works with HTTP or WebSocket protocol types (or anything that
    provides a "headers" entry in the scope).

    Requires the CookieMiddleware to be higher up in the stack.
    """

    def __init__(self, inner):
        self.inner = inner

    async def __call__(self, scope, receive, send):
        """
        Instantiate a session wrapper for this scope, resolve the session and
        call the inner application.
        """
        # 在 scope 中添加 session 值
        wrapper = InstanceSessionWrapper(scope, send)
        # 设置 session 懒加载对象的值
        await wrapper.resolve_session()

        return await self.inner(wrapper.scope, receive, wrapper.send)


# Shortcut to include cookie middleware
def SessionMiddlewareStack(inner):
    # 1. 先在 scope 中添加 cookies
    # 2. 再在 scope 中添加 session
    return CookieMiddlewareDecorator(SessionMiddlewareDecorator(inner))
