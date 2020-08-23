# -*- coding: utf-8 -*-


class _NoopLock(object):
    __slots__ = ()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass
