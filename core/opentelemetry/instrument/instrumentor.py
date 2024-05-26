import json
from typing import Collection

from django.conf import settings
from opentelemetry.instrumentation import dbapi
from opentelemetry.instrumentation.celery import CeleryInstrumentor
from opentelemetry.instrumentation.django import DjangoInstrumentor
from opentelemetry.instrumentation.instrumentor import BaseInstrumentor
from opentelemetry.instrumentation.logging import LoggingInstrumentor
from opentelemetry.instrumentation.redis import RedisInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from opentelemetry.trace import Span, Status, StatusCode, format_trace_id
from requests import Response


def requests_callback(span: Span, response: Response):
    """
    处理蓝鲸标准协议响应
    """
    try:
        json_result = response.json()
    except Exception:  # pylint: disable=broad-except
        return

    if not isinstance(json_result, dict):
        return

    # NOTE: esb has a result=bool, but apigateway or other backend maybe has no result
    code = json_result.get("code", 0)
    try:
        code = int(code)
    except Exception:  # pylint: disable=broad-except
        pass

    span.set_attribute("result_code", code)
    span.set_attribute("result_message", json_result.get("message", ""))

    errors = str(json_result.get("errors", ""))
    if errors:
        span.set_attribute("result_errors", errors)

    request_id = (
        # new esb and apigateway
        response.headers.get("x-bkapi-request-id")
        # iam backend
        or response.headers.get("x-request-id")
        # old esb
        or json_result.get("request_id", "")
    )
    if request_id:
        span.set_attribute("request_id", request_id)

    span.set_status(Status(StatusCode.OK if response.ok else StatusCode.ERROR))


def django_request_hook(span, request):
    """
    在request注入trace_id，方便获取
    """
    trace_id = span.get_span_context().trace_id
    request.otel_trace_id = format_trace_id(trace_id)


def django_response_hook(span, request, response):
    if hasattr(response, "data"):
        result = response.data
    else:
        try:
            result = json.loads(response.content)
        except Exception:  # pylint: disable=broad-except
            return
    if not isinstance(result, dict):
        return
    span.set_attribute("result_code", result.get("code", 0))
    span.set_attribute("result_message", result.get("message", ""))
    span.set_attribute("result_errors", result.get("errors", ""))
    result = result.get("result", True)
    if result:
        span.set_status(Status(StatusCode.OK))
        return
    span.set_status(Status(StatusCode.ERROR))


class DjangoAppInstrumentor(BaseInstrumentor):
    def instrumentation_dependencies(self) -> Collection[str]:
        return []

    def _instrument(self, **kwargs):
        LoggingInstrumentor().instrument()
        RequestsInstrumentor().instrument(span_callback=requests_callback)
        DjangoInstrumentor().instrument(request_hook=django_request_hook, response_hook=django_response_hook)
        CeleryInstrumentor().instrument()
        RedisInstrumentor().instrument()

        for instrumentor in settings.OPEN_TELEMETRY_OTEL_ADDTIONAL_INSTRUMENTORS:
            instrumentor.instrument()

        if settings.OPEN_TELEMETRY_OTEL_INSTRUMENT_DB_API:
            import MySQLdb  # noqa

            dbapi.wrap_connect(
                __name__,
                MySQLdb,
                "connect",
                "mysql",
                {"database": "db", "port": "port", "host": "host", "user": "user"},
            )

    def _uninstrument(self, **kwargs):
        for instrumentor in self.instrumentors:
            instrumentor.uninstrument()
