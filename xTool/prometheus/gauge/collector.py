# -*- coding: utf-8 -*-

import inspect


class GaugeCollector:

    def get_registry(self):
        """获得所有带有register装饰器的方法 ."""
        register_funcs = {}
        for name, value in inspect.getmembers(self, callable):
            if hasattr(value, "metric"):
                register_funcs[value.metric._name] = value

        return register_funcs
