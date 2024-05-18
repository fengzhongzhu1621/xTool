import os

import django
from django.conf import settings
from django.core.handlers.wsgi import WSGIHandler

from xTool.opentelemetry.metrics.server import start_metrics_http_server


def get_wsgi_application():
    """
    The public interface to Django's WSGI support. Should return a WSGI
    callable.

    Allows us to avoid making django.core.handlers.WSGIHandler public API, in
    case the internal WSGI implementation changes or moves in the future.
    """
    django.setup(set_prefix=False)

    if os.getenv("ENABLE_METRICS") or getattr(settings, "ENABLE_OTEL_METRICS", False):
        start_metrics_http_server()

    return WSGIHandler()
