from prometheus_client import Counter as BaseCounter

from xTool.opentelemetry_utils.collector import REGISTRY

from .label import LabelHandleMixin


class Counter(LabelHandleMixin, BaseCounter):
    def __init__(self, *args, registry=REGISTRY, **kwargs):
        self.args = args
        self.kwargs = kwargs
        super().__init__(*args, registry=registry, **kwargs)

    def set_registry(self, registry):
        return self.__class__(*self.args, registry=registry, **self.kwargs)
