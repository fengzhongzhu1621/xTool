# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from builtins import object


class BaseRule(object):
    @classmethod
    def is_valid(cls, rule):
        return rule in cls.all_rules()

    @classmethod
    def all_rules(cls):
        return [getattr(cls, attr)
                for attr in dir(cls)
                if not attr.startswith("__") and not callable(getattr(cls, attr))]
