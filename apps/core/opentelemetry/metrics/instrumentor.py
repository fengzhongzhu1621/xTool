from typing import Collection

from django import VERSION as django_version
from django.conf import settings
from opentelemetry.instrumentation.django.package import _instruments
from opentelemetry.instrumentation.instrumentor import BaseInstrumentor

from .middlewares import SaaSMetricsBeforeMiddleware, SaaSMetricsAfterMiddleware

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
    _after_middleware = ".".join([SaaSMetricsAfterMiddleware.__module__, SaaSMetricsAfterMiddleware.__qualname__])

    def instrumentation_dependencies(self) -> Collection[str]:
        return _instruments

    def _instrument(self, **kwargs):
        # This can not be solved, but is an inherent problem of this approach:
        # the order of middleware entries matters, and here you have no control
        # on that:
        # https://docs.djangoproject.com/en/3.0/topics/http/middleware/#activating-middleware
        # https://docs.djangoproject.com/en/3.0/ref/middleware/#middleware-ordering

        _middleware_setting = _get_django_middleware_setting()
        settings_middleware = getattr(settings, _middleware_setting, [])

        # Django allows to specify middlewares as a tuple, so we convert this tuple to a
        # list, otherwise we wouldn't be able to call append/remove
        if isinstance(settings_middleware, tuple):
            settings_middleware = list(settings_middleware)

        settings_middleware.insert(0, self._before_middleware)
        settings_middleware.append(self._after_middleware)
        setattr(settings, _middleware_setting, settings_middleware)

    def _uninstrument(self, **kwargs):
        _middleware_setting = _get_django_middleware_setting()
        settings_middleware = getattr(settings, _middleware_setting, None)

        if settings_middleware is None or (
            self._before_middleware not in settings_middleware and self._after_middleware not in settings_middleware
        ):
            return

        settings_middleware.remove(self._before_middleware)
        settings_middleware.remove(self._after_middleware)
        setattr(settings, _middleware_setting, settings_middleware)
