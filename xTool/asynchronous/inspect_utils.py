import six

if six.PY34:
    import asyncio  # pylint: disable=import-error,g-import-not-at-top  # pytype: disable=import-error


def is_coroutine_function(fn):
    try:
        return six.PY34 and asyncio.iscoroutinefunction(fn)
    except:  # pylint: disable=bare-except # noqa
        return False
