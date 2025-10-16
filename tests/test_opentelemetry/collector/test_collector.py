from prometheus_client import CollectorRegistry, Counter, Metric


def test_get_metrics():
    # 创建一个计数器指标
    counter = Counter("my_counter", "This is a sample counter")

    # 增加计数器的值
    counter.inc()

    # 创建一个 CollectorRegistry 实例
    registry = CollectorRegistry()

    # 将计数器指标注册到 registry
    registry.register(counter)

    # 获取注册表中的所有度量指标
    metrics = registry.collect()
    for metric in metrics:
        assert type(metric) == Metric
