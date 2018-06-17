# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from builtins import object


class BaseRule(object):

    _ALL_RULES = {}

    @classmethod
    def is_valid(cls, rule):
        return rule in cls.all_rules()

    @classmethod
    def all_rules(cls):
        if not cls._ALL_RULES:
            # 获得属性值集合
            cls._ALL_RULES = {
                getattr(cls, attr)
                for attr in dir(cls)
                if not attr.startswith("_") and not callable(getattr(cls, attr))
            }
        return cls._ALL_RULES
