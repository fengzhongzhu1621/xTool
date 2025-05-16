import os

from celery.utils.serialization import strtobool

from config import APP_CODE

OPEN_TELEMETRY_ENABLE_OTEL_METRICS = bool(strtobool(os.getenv("OPEN_TELEMETRY_ENABLE_OTEL_METRICS", "False")))
OPEN_TELEMETRY_ENABLE_OTEL_TRACE = bool(strtobool(os.getenv("OPEN_TELEMETRY_ENABLE_OTEL_TRACE", "False")))
OPEN_TELEMETRY_OTEL_INSTRUMENT_DB_API = bool(strtobool(os.getenv("OPEN_TELEMETRY_OTEL_INSTRUMENT_DB_API", "False")))
OPEN_TELEMETRY_OTEL_SERVICE_NAME = os.getenv("OPEN_TELEMETRY_OTEL_SERVICE_NAME") or APP_CODE

OPEN_TELEMETRY_OTEL_ADDTIONAL_INSTRUMENTORS = []
OPEN_TELEMETRY_OTEL_LOGGING_TRACE_FORMAT = (
    "[trace_id]: %(otelTraceID)s [span_id]: %(otelSpanID)s [resource.service.name]: %(otelServiceName)s"
)
