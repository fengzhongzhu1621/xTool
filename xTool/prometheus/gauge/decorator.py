import functools
from typing import Iterable

from prometheus_client import Gauge


def register(
    name: str = None,
    documentation: str = "",
    labelnames: Iterable[str] = (),
):

    def wrapper(func):
        metric_name = name if name else func.__name__
        metric_documentation = documentation if documentation else func.__doc__
        metric_documentation = metric_documentation.strip() if metric_documentation else ""
        metric = Gauge(name=metric_name, documentation=metric_documentation, labelnames=labelnames)

        @functools.wraps(func)
        def inner_wrapper(_self):
            # 每次执行清空
            if hasattr(metric, "_lock"):
                with metric._lock:
                    metric._metrics = {}
            metric._metric_init()
            # 对metric进行后续处理
            func(_self, metric)
            return metric

        # 打上标记，用户判断函数是否添加了装饰器
        inner_wrapper.metric = metric

        return inner_wrapper

    return wrapper
