# -*- coding: utf-8 -*-


class Proxy(object):
    """
    Create a proxy or placeholder for another object.
    """
    __slots__ = ('obj', '_callbacks')

    def __init__(self):
        self.obj = None
        self._callbacks = []
        self.initialize(None)

    def initialize(self, obj):
        self.obj = obj
        for callback in self._callbacks:
            callback(obj)

    def attach_callback(self, callback):
        self._callbacks.append(callback)
        return callback

    def pass_through(method):
        def inner(self, *args, **kwargs):
            if self.obj is None:
                raise AttributeError('Cannot use uninitialized Proxy.')
            return getattr(self.obj, method)(*args, **kwargs)
        return inner

    # Allow proxy to be used as a context-manager.
    __enter__ = pass_through('__enter__')
    __exit__ = pass_through('__exit__')

    def __getattr__(self, attr):
        if self.obj is None:
            raise AttributeError('Cannot use uninitialized Proxy.')
        return getattr(self.obj, attr)

    def __setattr__(self, attr, value):
        if attr not in self.__slots__:
            raise AttributeError('Cannot set attribute on proxy.')
        return super(Proxy, self).__setattr__(attr, value)
