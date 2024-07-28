import django
from django.conf import settings
from django.core.handlers.asgi import ASGIHandler
from django.core.handlers.wsgi import WSGIHandler

from xTool.opentelemetry_utils.metrics.server import start_metrics_http_server


def get_wsgi_application():
    """
    The public interface to Django's WSGI support. Should return a WSGI
    callable.

    Allows us to avoid making django.core.handlers.WSGIHandler public API, in
    case the internal WSGI implementation changes or moves in the future.
    """
    django.setup(set_prefix=False)

    if settings.OPEN_TELEMETRY_ENABLE_OTEL_METRICS:
        start_metrics_http_server()

    return WSGIHandler()


def get_asgi_application():
    """
    The public interface to Django's ASGI support. Return an ASGI 3 callable.

    Avoids making django.core.handlers.ASGIHandler a public API, in case the
    internal implementation changes or moves in the future.
    """
    django.setup(set_prefix=False)
    return ASGIHandler()
