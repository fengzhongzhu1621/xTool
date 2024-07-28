import arrow

# Use timer that's not susceptible to time of day adjustments.
try:
    # perf_counter is only present on Py3.3+
    from time import perf_counter as time_now  # noa
except ImportError:
    # fall back to using time
    from time import time as time_now  # noqa


def now() -> arrow.Arrow:
    return arrow.now()
