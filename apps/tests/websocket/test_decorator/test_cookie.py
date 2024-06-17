import pytest

from apps.websocket.decorator.cookie import CookieMiddlewareDecorator


@pytest.mark.asyncio
async def test_set_cookie():
    message = {}
    CookieMiddlewareDecorator.set_cookie(message, "Testing-Key", value="testing-value")
    assert message == {"headers": [(b"Set-Cookie", b"Testing-Key=testing-value; Path=/; SameSite=lax")]}
