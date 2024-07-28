from datetime import datetime, timedelta
from timeit import default_timer


def Time():
    """Returns some representation of the current time.

    This wrapper is meant to take advantage of a higher time
    resolution when available. Thus, its return value should be
    treated as an opaque object. It can be compared to the current
    time with TimeSince().
    """
    return default_timer()


def TimeSince(t):
    """Compares a value returned by Time() to the current time.

    Returns:
      the time since t, in fractional seconds.
    """
    return default_timer() - t


def days_ago(n, hour=0, minute=0, second=0, microsecond=0):
    """
    Get a datetime object representing `n` days ago. By default the time is
    set to midnight.
    """
    today = datetime.today().replace(hour=hour, minute=minute, second=second, microsecond=microsecond)
    return today - timedelta(days=n)


def ds_add(ds, days):
    """
    Add or subtract days from a YYYY-MM-DD

    :param ds: anchor date in ``YYYY-MM-DD`` format to add to
    :type ds: str
    :param days: number of days to add to the ds, you can use negative values
    :type days: int

    >>> ds_add('2015-01-01', 5)
    '2015-01-06'
    >>> ds_add('2015-01-06', -5)
    '2015-01-01'
    """

    ds = datetime.strptime(ds, "%Y-%m-%d")
    if days:
        ds = ds + timedelta(days)
    return ds.isoformat()[:10]
