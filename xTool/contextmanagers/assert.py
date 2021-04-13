# -*- coding: utf-8 -*-


class assert_raises(object):
    """A context manager that asserts a given exception was raised.

    >>> with assert_raises(TypeError):
    ...     raise TypeError

    >>> with assert_raises(TypeError):
    ...     raise ValueError
    AssertionError: ValueError not in ['TypeError']

    >>> with assert_raises(TypeError):
    ...     pass
    AssertionError: No exception raised.

    Or you can specify any of a number of exceptions:

    >>> with assert_raises(TypeError, ValueError):
    ...     raise ValueError

    >>> with assert_raises(TypeError, ValueError):
    ...     raise KeyError
    AssertionError: KeyError not in ['TypeError', 'ValueError']

    You can also get the exception back later:

    >>> with assert_raises(TypeError) as cm:
    ...     raise TypeError('bad type!')
    >>> cm.exception
    TypeError('bad type!')
    >>> cm.exc_type
    TypeError
    >>> cm.traceback
    <traceback @ 0x3323ef0>

    Lowercase name because that it's a class is an implementation detail.

    """

    def __init__(self, *exc_cls):
        self.exc_cls = exc_cls

    def __enter__(self):
        # For access to the exception later.
        return self

    def __exit__(self, typ, value, tb):
        assert typ, 'No exception raised.'
        assert typ in self.exc_cls, '%s not in %s' % (
            typ.__name__, [e.__name__ for e in self.exc_cls])
        self.exc_type = typ
        self.exception = value
        self.traceback = tb

        # Swallow expected exceptions.
        return True
