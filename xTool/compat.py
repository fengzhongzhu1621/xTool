import atexit
import itertools
import logging
import operator
import socket
import sys

import six

PY2 = sys.version_info[0] == 2
PY3 = sys.version_info[0] >= 3

PY34 = sys.version_info >= (3, 4)
PY35 = sys.version_info >= (3, 5)
PY352 = sys.version_info >= (3, 5, 2)
PY_36 = sys.version_info >= (3, 6)
PY_37 = sys.version_info >= (3, 7)
PY_38 = sys.version_info >= (3, 8)

IS_HPUX = sys.platform.startswith("hp-ux")
# Specifies whether the current runtime is HP-UX.
IS_LINUX = sys.platform.startswith("linux")
# Specifies whether the current runtime is HP-UX.
IS_UNIX = hasattr(socket, "AF_UNIX")

dataclass_kwargs = {}
if sys.version_info >= (3, 10):
    dataclass_kwargs.update({"slots": True})


# Specifies whether the current runtime is *NIX.


def _identity(x):
    return x


try:  # Python 2.7+
    from logging import NullHandler
except ImportError:

    class NullHandler(logging.Handler):
        def emit(self, record):
            pass


try:
    import grp
    import pwd
except ImportError:
    pwd = grp = None

try:
    from collections.abc import Mapping
except ImportError:
    from collections.abc import Mapping  # noqa

try:
    callable
except NameError:

    def callable(object):
        return hasattr(object, "__call__")


try:
    callable
except NameError:

    def callable(object):
        return hasattr(object, "__call__")


if PY3:
    try:
        from queue import SimpleQueue  # noqa
    except ImportError:
        from queue import Queue as SimpleQueue  # type: ignore # noqa

# Python 3.x (and backports) use a modified iterator syntax
# This will allow 2.x to behave with 3.x iterators
if not hasattr(__builtins__, "next"):

    def next(iter):
        try:
            # Try new style iterators
            return iter.__next__()
        except AttributeError:
            # Fallback in case of a "native" iterator
            return iter.next()


# Python < 2.5 does not have "any"
if not hasattr(__builtins__, "any"):

    def any(iterator):
        for item in iterator:
            if item:
                return True
        return False


# Random numbers for rotation temp file names, using secrets module if available (Python 3.6).
# Otherwise use `random.SystemRandom` if available, then fall back on
# `random.Random`.
try:
    # noinspection PyPackageRequirements,PyCompatibility
    from secrets import randbits
except ImportError:
    import random

    if hasattr(random, "SystemRandom"):  # May not be present in all Python editions
        # Should be safe to reuse `SystemRandom` - not software state dependant
        randbits = random.SystemRandom().getrandbits
    else:

        def randbits(nb):
            return random.Random().getrandbits(nb)


b = sys.version_info[0] < 3 and (lambda x: x) or (lambda x: x.encode("latin1"))

if PY3:
    import builtins
    import functools

    try:
        from collections.abc import Callable
    except ImportError:
        from collections.abc import Callable  # noqa

    reduce = functools.reduce
    zip = builtins.zip
    xrange = builtins.range
    map = builtins.map
    get_self = operator.attrgetter("__self__")
    get_func = operator.attrgetter("__func__")
    text = str
    text_type = str
    bytes_type = bytes
    buffer_type = memoryview
    string_types = (str,)
    integer_types = (int,)
    basestring = str
    long = int
    unicode_type = str
    basestring_type = str
    print_ = getattr(builtins, "print")
    izip_longest = itertools.zip_longest
    implements_to_string = _identity
    xrange = range

    def iterkeys(d):
        return iter(d.keys())

    def itervalues(d):
        return iter(d.values())

    def iteritems(d):
        return iter(d.items())

    def callable_(c):
        return isinstance(c, Callable)

    def reraise(tp, value, tb=None):
        """
        Examples:
            reraise(*sys.exc_info())

            try:
                1/0
            except Exception as err: # pylint: disable=broad-except
                error = err.with_traceback(sys.exc_info()[2]
                raise error
        """
        if value.__traceback__ is not tb:
            raise value.with_traceback(tb)
        raise value

    def raise_exc_info(exc_info):
        try:
            raise exc_info[1].with_traceback(exc_info[2])
        finally:
            exc_info = None

else:
    import itertools

    import __builtin__

    builtins = __builtin__
    reduce = __builtin__.reduce
    zip = itertools.izip
    xrange = __builtin__.xrange
    map = itertools.imap
    get_self = operator.attrgetter("im_self")
    get_func = operator.attrgetter("im_func")
    text = (str, unicode)  # noqa
    text_type = unicode  # noqa
    bytes_type = str
    buffer_type = buffer  # noqa
    string_types = (str, unicode)  # noqa
    integer_types = (int, long)  # noqa
    unicode_type = unicode  # noqa
    basestring_type = basestring  # noqa
    izip_longest = itertools.izip_longest
    callable_ = callable

    def iterkeys(d):
        return d.iterkeys()

    def itervalues(d):
        return d.itervalues()

    def iteritems(d):
        return d.iteritems()

    exec("def reraise(tp, value, tb=None):\n raise tp, value, tb")

    exec(
        """
def raise_exc_info(exc_info):
    raise exc_info[0], exc_info[1], exc_info[2]
"""
    )

    def print_(s):
        sys.stdout.write(s)
        sys.stdout.write("\n")

    def implements_to_string(cls):
        cls.__unicode__ = cls.__str__
        cls.__str__ = lambda x: x.__unicode__().encode("utf-8")
        return cls

    FileNotFoundError = EnvironmentError

try:
    from sys import is_finalizing
except ImportError:
    # Emulate it
    def _get_emulated_is_finalizing():
        L = []
        atexit.register(lambda: L.append(None))

        def is_finalizing():
            # Not referencing any globals here
            return L != []

        return is_finalizing

    is_finalizing = _get_emulated_is_finalizing()


def with_metaclass(meta, *bases):
    # This requires a bit of explanation: the basic idea is to make a
    # dummy metaclass for one level of class instantiation that replaces
    # itself with the actual metaclass.  Because of internal type checks
    # we also need to make sure that we downgrade the custom metaclass
    # for one level to something closer to type (that's why __call__ and
    # __init__ comes back from type etc.).
    #
    # This has the advantage over six.with_metaclass in that it does not
    # introduce dummy classes into the final MRO.
    class metaclass(meta):
        __call__ = type.__call__
        __init__ = type.__init__

        def __new__(cls, name, this_bases, d):
            if this_bases is None:
                return type.__new__(cls, name, (), d)
            return meta(name, bases, d)

    return metaclass("temporary_class", None, {})


def flatten_list_bytes(list_of_data):
    """Concatenate a sequence of bytes-like objects."""
    if not PY34:
        # On Python 3.3 and older, bytes.join() doesn't handle
        # memoryview.
        list_of_data = (bytes(data) if isinstance(data, memoryview) else data for data in list_of_data)
    return b"".join(list_of_data)


def qualname(x):
    if six.PY34:
        return x.__qualname__

    # not perfect - but it is ok for cache key
    if hasattr(x, "im_class"):
        return ".".join((x.im_class.__name__, x.__name__))
    else:
        return x.__name__
