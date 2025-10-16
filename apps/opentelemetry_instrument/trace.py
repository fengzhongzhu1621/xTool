from contextlib import contextmanager

from django.conf import settings
from opentelemetry.trace import get_tracer

from apps.logger import logger


@contextmanager
def start_new_span(func):
    """
    开启一个新的span，同时也会生成新的 trace ID
    为了解决调用apply_async()任务时，trace_id 都是同一个的问题
    """
    if settings.OPEN_TELEMETRY_ENABLE_OTEL_TRACE:
        logger.error("Start a new span")
        with get_tracer(__name__).start_as_current_span(func.__name__) as span:
            logger.error("Span is active with trace ID:", span.get_span_context().trace_id)
            yield span
    else:
        yield
