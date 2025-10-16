import threading

from .noop import NoopLock


def create_threading_lock(thread_safe=True):
    if thread_safe:
        lock = threading.Lock()
    else:
        lock = NoopLock()
    return lock
