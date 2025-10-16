from contextlib import contextmanager

from django.utils import translation


@contextmanager
def respect_language(language):
    """Context manager that changes the current translation language for
    all code inside the following block.
    """
    if language:
        prev = translation.get_language()
        translation.activate(language)
        try:
            yield
        finally:
            translation.activate(prev)
    else:
        yield
