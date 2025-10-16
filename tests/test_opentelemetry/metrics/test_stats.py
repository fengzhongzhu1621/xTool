import time
from unittest import TestCase

from statsd import StatsClient

from xTool.opentelemetry_utils.metrics.stats import SafeStatsdLogger, StatsParamConfig, get_stats_logger


class TestSafeStatsdLogger(TestCase):
    def setUp(self) -> None:
        statsd_client = StatsClient(host="localhost", port=8125, prefix="test.statsd", maxudpsize=512)
        self.stats_logger = SafeStatsdLogger(statsd_client)

    def test_incr(self):
        self.stats_logger.incr("request_times.interfaceA", count=1, rate=1)
        self.stats_logger.incr("request_times.interfaceA", count=2, rate=0.9)
        self.stats_logger.incr("request_times.interfaceA", count=7, rate=0.9)
        self.stats_logger.incr("request_times.interfaceA", count=10, rate=0.9)

    def test_time(self):
        for i in range(10):
            with self.stats_logger.timer("test_time.sleep1"):
                time.sleep(0.1)

    def test_gauge(self):
        self.stats_logger.gauge("test_gauge", 70)  # Set the 'foo' gauge to 70.
        self.stats_logger.gauge("test_gauge", 1, delta=True)  # Set 'foo' to 71.
        self.stats_logger.gauge("test_gauge", -3, delta=True)  # Set 'foo' to 68.

    def test_set(self):
        self.stats_logger.set("test_set", "user0")
        self.stats_logger.set("test_set", "user1")
        self.stats_logger.set("test_set", "user1")
        self.stats_logger.set("test_set", "user2")
        self.stats_logger.set("test_set", "user2")
        self.stats_logger.set("test_set", "user2")


def test_get_stats_logger():
    stats_logger = get_stats_logger("statsd")

    # 设置客户端
    statsd_config = StatsParamConfig()
    stats_logger.create_client(statsd_config)

    # 设置验证器
    stats_name_config = None
    allow_name_validator_config = None
    stats_logger.set_validator(stats_name_config, allow_name_validator_config)

    stats_logger.incr("request_times.interfaceA", count=1, rate=1)
    stats_logger.incr("request_times.interface*", count=1, rate=1)
