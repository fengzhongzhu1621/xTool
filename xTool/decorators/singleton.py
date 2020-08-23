# -*- coding: utf-8 -*-

from functools import wraps


def singleton(cls):
    """装饰类，用于单例模式 ."""
    instances = {}

    @wraps(cls)
    def get_instance(*args, **kwargs):
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]

    return get_instance
