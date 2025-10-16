"""
代理模式
"""


class Proxy:
    """
    Create a proxy or placeholder for another object.
    """

    __slots__ = ("obj", "_callbacks")

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

    def pass_through(method: str):
        """装饰器，用于被代理的对象方法 ."""

        def inner(self, *args, **kwargs):
            if self.obj is None:
                raise AttributeError("Cannot use uninitialized Proxy.")
            return getattr(self.obj, method)(*args, **kwargs)

        return inner

    # Allow proxy to be used as a context-manager.
    __enter__ = pass_through("__enter__")
    __exit__ = pass_through("__exit__")

    def __getattr__(self, attr):
        """获得被代理对象的属性 ."""
        if self.obj is None:
            raise AttributeError("Cannot use uninitialized Proxy.")
        return getattr(self.obj, attr)

    def __setattr__(self, attr, value):
        """修改被代理对象的值 ."""
        if attr not in self.__slots__:
            raise AttributeError("Cannot set attribute on proxy.")
        return super().__setattr__(attr, value)
