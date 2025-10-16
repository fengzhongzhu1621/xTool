"""
WSGI config for apps project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/howto/deployment/wsgi/
"""

import os

from core.wsgi import get_wsgi_application

# Django 支持编写异步（“async”）视图，如果在 ASGI 下运行，还支持完全异步的请求堆栈。
# 异步视图仍然可以在 WSGI 下运行，但会有性能损失，并且不能有高效的长时间运行的请求。
#
# 1. 如果确实需要使用异步功能，应该确保你的Django版本至少是3.1，并且设置 DJANGO_ALLOW_ASYNC_UNSAFE=1。
# 2. 如果不需要使用异步功能，应该移除所有的异步不安全的操作，包括异步视图和异步中间件，并确保项目只使用Django支持的同步操作。
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")
# 支持异步
os.environ["DJANGO_ALLOW_ASYNC_UNSAFE"] = "true"

application = get_wsgi_application()
