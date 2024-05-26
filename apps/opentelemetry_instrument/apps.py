from django.apps import AppConfig

from core.opentelemetry.setup import setup_by_settings


class InstrumentAppConfig(AppConfig):
    name = "apps.opentelemetry_instrument"

    def ready(self):
        setup_by_settings()
        from .celery import worker_process_init_otel_trace_setup  # noqa
