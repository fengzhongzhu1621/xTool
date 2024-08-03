import random

from xTool.time_utils.retry.retring import retry


@retry
def do_something_unreliable():
    if random.randint(0, 10) > 1:
        raise OSError("Broken sauce, everything is hosed!!!111one")
    else:
        return "Awesome sauce!"


def test_do_something_unreliable():
    do_something_unreliable()
