# -*- coding: utf-8 -*-
import time


class InstanceCache:
    """基于内存的缓冲 ."""

    @classmethod
    def instance(cls, *args, **kwargs):
        if not hasattr(cls, "_instance"):
            cls._instance = cls()
        return cls._instance

    def __init__(self):
        self.__cache = {}

    def clear(self):
        self.__cache = {}

    def set(self, key, value, seconds=0, use_round=False):
        """
        :param key:
        :param value:
        :param seconds: 秒
        :param use_round: 时间是否需要向上取整，取整用于缓存时间同步
        :return:
        """
        if not use_round:
            timeout = time.time() + seconds
        else:
            timeout = (time.time() + seconds) // seconds * seconds
        self.__cache[key] = (value, timeout)

    def __get_raw(self, key):
        value = self.__cache.get(key)
        if not value:
            return None
        if value[1] and time.time() > value[1]:
            del self.__cache[key]
            return None
        return value

    def exists(self, key):
        value = self.__get_raw(key)
        return value is not None

    def get(self, key):
        value = self.__get_raw(key)
        return value and value[0]

    def delete(self, key):
        try:
            del self.__cache[key]
        except KeyError:
            pass
