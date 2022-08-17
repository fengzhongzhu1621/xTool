# -*- coding: utf-8 -*-
from unittest import TestCase
from xTool.prometheus.gauge.collector import GaugeCollector
from xTool.prometheus.gauge.decorator import register


class GaugeCollectorCase(GaugeCollector):

    @register()
    def register_a(self, metric):
        """a register"""
        pass


class TestGaugeCollector(TestCase):

    def setUp(self) -> None:
        self.collector = GaugeCollectorCase()

    def test_registry(self):
        funcs = self.collector.get_registry()
        assert "register_a" in funcs

    def test_get_metrics(self):
        metrics = self.collector.get_metrics()
        assert [metric._name for metric in metrics] == ["register_a"]

    def test_get_metric_names(self):
        actual = self.collector.get_metric_names()
        assert actual == ["register_a"]

    def test_generate_latest(self):
        actual = self.collector.generate_latest()
        expect = '# HELP register_a a register\n# TYPE register_a gauge\nregister_a 0.0\n'
        assert actual == expect

    def test_get_samples(self):
        samples = self.collector.get_samples()
        actual = [dict(sample._asdict()) for sample in samples]
        expect = [
            {
                'exemplar': None,
                'labels': {},
                'name': 'register_a',
                'timestamp': None,
                'value': 0.0
            }
        ]
        assert actual == expect
