from typing import Collection

from django import VERSION as django_version
from django.conf import settings
from opentelemetry.instrumentation.django.package import _instruments
from opentelemetry.instrumentation.instrumentor import BaseInstrumentor

from .middlewares import SaaSMetricsAfterMiddleware, SaaSMetricsBeforeMiddleware

DJANGO_2_0 = django_version >= (2, 0)


def _get_django_middleware_setting() -> str:
    # In Django versions 1.x, setting MIDDLEWARE_CLASSES can be used as a legacy
    # alternative to MIDDLEWARE. This is the case when `settings.MIDDLEWARE` has
    # its default value (`None`).
    if not DJANGO_2_0 and getattr(settings, "MIDDLEWARE", None) is None:
        return "MIDDLEWARE_CLASSES"
    return "MIDDLEWARE"


class SaaSMetricsInstrumentor(BaseInstrumentor):

    _before_middleware = ".".join(
        [
            SaaSMetricsBeforeMiddleware.__module__,
            SaaSMetricsBeforeMiddleware.__qualname__,
        ]
    )
    _after_middleware = ".".join(
        [
            SaaSMetricsAfterMiddleware.__module__,
            SaaSMetricsAfterMiddleware.__qualname__,
        ]
    )

    def instrumentation_dependencies(self) -> Collection[str]:
        """需要的依赖支持 ."""
        return _instruments

    def _instrument(self, **kwargs):
        """动态增加中间件 ."""
        settings_middleware = settings.MIDDLEWARE
        settings_middleware = list(settings_middleware)

        settings_middleware.insert(0, self._before_middleware)
        settings_middleware.append(self._after_middleware)
        setattr(settings, "MIDDLEWARE", settings_middleware)

    def _uninstrument(self, **kwargs):
        settings_middleware = settings.MIDDLEWARE

        if settings_middleware is None or (
            self._before_middleware not in settings_middleware and self._after_middleware not in settings_middleware
        ):
            return

        settings_middleware.remove(self._before_middleware)
        settings_middleware.remove(self._after_middleware)
        setattr(settings, "MIDDLEWARE", settings_middleware)
