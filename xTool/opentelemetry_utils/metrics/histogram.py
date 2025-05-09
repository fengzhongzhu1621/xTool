from prometheus_client import Histogram as BaseHistogram
from prometheus_client.utils import INF

from xTool.opentelemetry_utils.collector import REGISTRY

from .label import LabelHandleMixin


class Histogram(LabelHandleMixin, BaseHistogram):
    DEFAULT_BUCKETS = (0.005, 0.01, 0.05, 0.1, 0.5, 1.0, 2.5, 5.0, 7.5, 10.0, 30.0, INF)

    def __init__(self, *args, registry=REGISTRY, buckets=DEFAULT_BUCKETS, **kwargs):
        self.args = args
        self.kwargs = kwargs
        self.buckets = buckets
        super().__init__(*args, registry=registry, buckets=buckets, **kwargs)

    def set_registry(self, registry):
        return self.__class__(*self.args, registry=registry, buckets=self.buckets, **self.kwargs)
