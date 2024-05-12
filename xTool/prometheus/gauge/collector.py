import inspect
import itertools
from typing import List

from prometheus_client.exposition import generate_latest


class GaugeCollector:

    def get_registry(self):
        """获得所有带有register装饰器的方法 ."""
        register_funcs = {}
        for name, value in inspect.getmembers(self, callable):
            if hasattr(value, "metric"):
                register_funcs[value.metric._name] = value

        return register_funcs

    def get_metrics(self):
        metrics = []
        for _, func in self.get_registry().items():
            metrics.append(func.metric)
        return metrics

    def get_metric_names(self) -> List:
        registry = self.get_registry()
        return list(registry.keys())

    def generate_latest(self):
        metrics = self.get_metrics()
        result = "\n".join(generate_latest(metric).decode("utf-8") for metric in metrics)
        return result

    def get_samples(self):
        metrics = self.get_metrics()
        collected_metrics = [metric.collect() for metric in metrics]
        samples = []
        for collected_metric in itertools.chain(*collected_metrics):
            samples.extend(collected_metric.samples)
        return samples
