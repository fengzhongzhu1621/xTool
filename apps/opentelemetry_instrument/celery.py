from celery.signals import worker_process_init

from core.opentelemetry.setup import setup_by_settings


@worker_process_init.connect(weak=False)
def worker_process_init_otel_trace_setup(*args, **kwargs):
    setup_by_settings()
