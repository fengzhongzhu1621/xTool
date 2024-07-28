import sys

# sys.maxsize:
# An integer giving the maximum value a variable of type Py_ssize_t can take.
MAX_WAIT = sys.maxsize / 2


def PowersOf(logbase, count, lower=0, include_zero=True):
    """Returns a list of count powers of logbase (from logbase**lower)."""
    if not include_zero:
        return [logbase**i for i in range(lower, count + lower)]
    else:
        return [0] + [logbase**i for i in range(lower, count + lower)]
