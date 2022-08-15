# -*- coding: utf-8 -*-
from unittest import TestCase
from xTool.prometheus.gauge.collector import GaugeCollector
from xTool.prometheus.gauge.decorator import register


class GaugeCollectorCase(GaugeCollector):

    @register()
    def register_a(self, metric):
        "a register"
        pass


class TestCollector(TestCase):

    def setUp(self) -> None:
        pass

    def test_registry(self):
        collector = GaugeCollectorCase()
        funcs = collector.get_registry()
        assert "register_a" in funcs
