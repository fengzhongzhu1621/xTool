import os

from django.conf import settings

__all__ = [
    "get_service_name",
]


def get_service_name() -> str:
    app_module_name = getattr(settings, "APP_MODULE_NAME", "")
    service_name = (
        os.getenv("BKAPP_OTEL_SERVICE_NAME")
        or getattr(settings, "BKAPP_OTEL_SERVICE_NAME", None)
        or (settings.APP_CODE + f"-{app_module_name}" if app_module_name else "")
    )
    return service_name
