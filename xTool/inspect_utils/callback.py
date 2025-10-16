from typing import Any, Callable


def get_callback_name(cb: Callable[..., Any]) -> str:
    """Get a callback fully-qualified name.

    If no name can be produced ``repr(cb)`` is called and returned.
    """
    if cb is None:
        return "<unknown>"

    segments = []
    try:
        segments.append(cb.__qualname__)
    except AttributeError:
        try:
            segments.append(cb.__name__)
        except AttributeError:
            pass
    if not segments:
        return repr(cb)
    else:
        try:
            # When running under sphinx it appears this can be none?
            if cb.__module__:
                segments.insert(0, cb.__module__)
        except AttributeError:
            pass
        return ".".join(segments)
