# -*- coding: utf-8 -*-

import threading
from .noop import _NoopLock


def create_threading_lock(thread_safe=True):
    if thread_safe:
        lock = threading.Lock()
    else:
        lock = _NoopLock()
    return lock
