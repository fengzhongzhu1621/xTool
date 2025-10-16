from prometheus_client import Gauge as BaseGauge

from xTool.opentelemetry_utils.collector import REGISTRY

from .label import LabelHandleMixin


class Gauge(LabelHandleMixin, BaseGauge):
    def __init__(self, *args, registry=REGISTRY, **kwargs):
        self.args = args
        self.kwargs = kwargs
        super().__init__(*args, registry=registry, **kwargs)

    def set_registry(self, registry):
        return self.__class__(*self.args, registry=registry, **self.kwargs)
