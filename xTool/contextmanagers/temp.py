from contextlib import contextmanager
from pathlib import Path
from tempfile import TemporaryDirectory


@contextmanager
def temp_path(name):
    """a simple cross platform replacement for NamedTemporaryFile"""
    with TemporaryDirectory() as td:
        yield Path(td, name)
