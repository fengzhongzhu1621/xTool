import os
import socket

from django.conf import settings
from django_prometheus.middleware import (
    Metrics,
    PrometheusAfterMiddleware,
    PrometheusBeforeMiddleware,
)
from django_prometheus.utils import Time, TimeSince

HOSTNAME = socket.gethostname()
BK_ENV = os.getenv("ENVIRONMENT", "dev")


class CustomMetrics(Metrics):

    def register_metric(self, metric_cls, name, documentation, labelnames=(), **kwargs):
        """所有上报的 metric 增加 3 个标签 ."""
        return super().register_metric(
            metric_cls, name, documentation, labelnames=[*labelnames, "hostname", "bk_env", "bk_app_code"], **kwargs
        )


class SaaSMetricsBeforeMiddleware(PrometheusBeforeMiddleware):
    metrics_cls = CustomMetrics

    def process_request(self, request):
        """设置自定义标签的值  ."""
        # 上报请求次数
        self.metrics.requests_total.labels(hostname=HOSTNAME, bk_env=BK_ENV, bk_app_code=settings.APP_CODE).inc()
        request.prometheus_before_middleware_event = Time()

    def process_response(self, request, response):
        self.metrics.responses_total.labels(hostname=HOSTNAME, bk_env=BK_ENV, bk_app_code=settings.APP_CODE).inc()
        if hasattr(request, "prometheus_before_middleware_event"):
            # 上报请求处理时间（秒）
            self.metrics.requests_latency_before.labels(
                hostname=HOSTNAME, bk_env=BK_ENV, bk_app_code=settings.APP_CODE
            ).observe(TimeSince(request.prometheus_before_middleware_event))
        else:
            self.metrics.requests_unknown_latency_before.labels(
                hostname=HOSTNAME, bk_env=BK_ENV, bk_app_code=settings.APP_CODE
            ).inc()
        return response


class SaaSMetricsAfterMiddleware(PrometheusAfterMiddleware):
    metrics_cls = CustomMetrics

    def label_metric(self, metric, request, response=None, **labels):
        labels.update({"hostname": HOSTNAME, "bk_env": BK_ENV, "bk_app_code": settings.APP_CODE})
        return super().label_metric(metric, request, response=response, **labels)
