import threading
from typing import Callable


class defaultlocal(threading.local):
    """
    Thread local storage with default values for each field in each thread

    >>>
    >>> l = defaultlocal( foo=42 )
    >>> def f(): print(l.foo)
    >>> t = threading.Thread(target=f)
    >>> t.start() ; t.join()
    42
    """

    def __init__(self, **kwargs):
        super().__init__()
        self.__dict__.update(kwargs)


def go(func: Callable) -> Callable:
    """将函数转换为异步执行 ."""

    def wrapper(*args, **kwargs):
        t = threading.Thread(target=func, args=args, kwargs=kwargs)
        t.start()
        return t

    return wrapper
