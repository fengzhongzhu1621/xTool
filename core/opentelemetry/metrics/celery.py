from celery.bootsteps import StartStopStep

from xTool.opentelemetry_utils.metrics.server import start_metrics_http_server


class MetricsServerStep(StartStopStep):
    requires = {"celery.worker.components:Timer"}
    _reporter = None

    def start(self, worker):
        start_metrics_http_server()

    @classmethod
    def setup_reporter(cls, reporter):
        cls._reporter = reporter
