# -*- coding: utf-8 -*-

from unittest import TestCase
from statsd import StatsClient
from xTool.metrics.stats import SafeStatsdLogger


class TestSafeStatsdLogger(TestCase):
    def setUp(self) -> None:
        statsd_client = StatsClient(host='localhost', port=8125, prefix=None, maxudpsize=512)
        self.stats_logger = SafeStatsdLogger(statsd_client)

    def test_incr(self):
        pass
