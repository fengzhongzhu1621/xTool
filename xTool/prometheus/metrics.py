import time
from contextlib import contextmanager

from prometheus_client import Histogram

LATENCY_BUCKETS = (
    0.01,
    0.025,
    0.05,
    0.075,
    0.1,
    0.25,
    0.5,
    0.75,
    1.0,
    2.5,
    5.0,
    7.5,
    10.0,
    25.0,
    50.0,
    75.0,
    float("inf"),
)


@contextmanager
def observe(histogram: Histogram, **labels):
    """记录耗时 ."""
    start = time.time()
    yield
    histogram.labels(**labels).observe(time.time() - start)
