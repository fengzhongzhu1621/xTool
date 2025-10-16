import os

from django.conf import settings
from django.utils.log import configure_logging
from opentelemetry import trace
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.sampling import _KNOWN_SAMPLERS

from config.celery import app as celery_app
from core.opentelemetry.export import LazyBatchSpanProcessor
from core.opentelemetry.instrument.instrumentor import DjangoAppInstrumentor
from core.opentelemetry.log import inject_logging_trace_info
from core.opentelemetry.metrics.celery import MetricsServerStep
from core.opentelemetry.metrics.instrumentor import SaaSMetricsInstrumentor


def setup_trace_config(
    service_name: str,
    bk_data_id: int,
    otel_sampler: str,
    otel_grpc_host: str,
    bk_data_token: str = "",
):
    span_processor = LazyBatchSpanProcessor
    if settings.ENVIRONMENT == "dev":
        # local environment, use jaeger as trace service
        # docker run -p 16686:16686 -p 6831:6831/udp jaegertracing/all-in-one
        trace.set_tracer_provider(TracerProvider(resource=Resource.create({SERVICE_NAME: service_name})))
        jaeger_exporter = JaegerExporter(agent_host_name="localhost", agent_port=6831, udp_split_oversized_batches=True)
        trace.get_tracer_provider().add_span_processor(span_processor(jaeger_exporter))
    else:
        # stage and prod environment, use bk_log as trace service
        trace.set_tracer_provider(
            tracer_provider=TracerProvider(
                resource=Resource.create(
                    {"service.name": service_name, "bk_data_id": bk_data_id, "bk.data.token": bk_data_token},
                ),
                sampler=_KNOWN_SAMPLERS[otel_sampler],
            )
        )
        otlp_exporter = OTLPSpanExporter(endpoint=otel_grpc_host)
        span_processor = span_processor(otlp_exporter)
        trace.get_tracer_provider().add_span_processor(span_processor)


def setup_by_settings():
    enable_trace = settings.OPEN_TELEMETRY_ENABLE_OTEL_TRACE
    if enable_trace:
        service_name = settings.OPEN_TELEMETRY_OTEL_SERVICE_NAME
        bk_data_id = int(os.getenv("OPENTELEMETRY_OTEL_BK_DATA_ID", 0))
        otel_sampler = os.getenv("OPENTELEMETRY_OTEL_SAMPLER")
        otel_grpc_host = os.getenv("OPENTELEMETRY_OTEL_GRPC_HOST")
        otel_bk_data_token = os.getenv("OPENTELEMETRY_OTEL_BK_DATA_TOKEN")
        setup_trace_config(service_name, bk_data_id, otel_sampler, otel_grpc_host, bk_data_token=otel_bk_data_token)
        DjangoAppInstrumentor().instrument()
        # 将Trace信息配置到项目日志中
        trace_format = settings.OPEN_TELEMETRY_OTEL_LOGGING_TRACE_FORMAT
        inject_logging_trace_info(settings.LOGGING, ("verbose",), trace_format)
        configure_logging(settings.LOGGING_CONFIG, settings.LOGGING)
    # metrics
    enable_metrics = settings.OPEN_TELEMETRY_ENABLE_OTEL_METRICS
    if enable_metrics:
        SaaSMetricsInstrumentor().instrument()
        # celery worker 启动时启动 metric http server
        celery_app.steps["worker"].add(MetricsServerStep)
