# -*- coding: utf-8 -*-

import time
from typing import Optional


class Timer:
    """
    Timer that records duration, and optional sends to statsd backend.

    This class lets us have an accurate timer with the logic in one place (so
    that we don't use datetime math for duration -- it is error prone).
    """
    _start_time: Optional[float]
    duration: Optional[float]

    def __init__(self, real_timer=None):
        self.real_timer = real_timer

    def __enter__(self):
        return self.start()

    def __exit__(self, exc_type, exc_value, traceback):
        self.stop()

    def start(self):
        """Start the timer"""
        if self.real_timer:
            self.real_timer.start()
        self._start_time = time.perf_counter()
        return self

    def stop(self, send=True):  # pylint: disable=unused-argument
        """Stop the timer, and optionally send it to stats backend"""
        self.duration: float = time.perf_counter() - self._start_time
        if send and self.real_timer:
            self.real_timer.stop()
