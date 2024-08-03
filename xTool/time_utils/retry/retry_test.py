import logging
import random
import sys

from xTool.time_utils.retry.log import *  # noqa
from xTool.time_utils.retry.retring import retry
from xTool.time_utils.retry.retry import *  # noqa
from xTool.time_utils.retry.stop import *  # noqa
from xTool.time_utils.retry.wait import *  # noqa

logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)

logger = logging.getLogger(__name__)


@retry
def do_something_unreliable():
    if random.randint(0, 10) > 1:
        raise OSError("Broken sauce, everything is hosed!!!111one")
    else:
        return "Awesome sauce!"


def test_do_something_unreliable():
    do_something_unreliable()


@retry(stop=stop_after_attempt(7))
def stop_after_7_attempts():
    print("Stopping after 7 attempts")
    raise Exception


@retry(stop=stop_after_delay(10))
def stop_after_10_s():
    print("Stopping after 10 seconds")
    raise Exception


@retry(stop=(stop_after_delay(10) | stop_after_attempt(5)))
def stop_after_10_s_or_5_retries():
    print("Stopping after 10 seconds or 5 retries")
    raise Exception


@retry(wait=wait_fixed(2))
def wait_2_s():
    print("Wait 2 second between retries")
    raise Exception


@retry(wait=wait_random(min=1, max=2))
def wait_random_1_to_2_s():
    print("Randomly wait 1 to 2 seconds between retries")
    raise Exception


@retry(wait=wait_fixed(3) + wait_random(0, 2))
def wait_fixed_jitter():
    print("Wait at least 3 seconds, and add up to 2 seconds of random delay")
    raise Exception


@retry(wait=wait_random_exponential(multiplier=1, max=60))
def wait_exponential_jitter():
    print(
        "Randomly wait up to 2^x * 1 seconds between each retry until the range reaches 60 seconds, then randomly up to 60 seconds afterwards"
    )
    raise Exception


@retry(wait=wait_chain(*[wait_fixed(3) for i in range(3)] + [wait_fixed(7) for i in range(2)] + [wait_fixed(9)]))
def wait_fixed_chained():
    print("Wait 3s for 3 attempts, 7s for the next 2 attempts and 9s for all attempts thereafter")
    raise Exception


class ClientError(Exception):
    """Some type of client error."""


@retry(retry=retry_if_exception_type(IOError))
def might_io_error():
    print("Retry forever with no wait if an IOError occurs, raise any other errors")
    raise Exception


@retry(retry=retry_if_not_exception_type(ClientError))
def might_client_error():
    print("Retry forever with no wait if any error other than ClientError occurs. Immediately raise ClientError.")
    raise Exception


def is_none_p(value):
    """Return True if value is None"""
    return value is None


@retry(retry=retry_if_result(is_none_p))
def might_return_none():
    print("Retry with no wait if return value is None")


def is_none_p(value):
    """Return True if value is None"""
    return value is None


@retry(retry=(retry_if_result(is_none_p) | retry_if_exception_type()))
def might_return_none_1():
    print("Retry forever ignoring Exceptions with no wait if return value is None")


class MyException(Exception):
    pass


@retry(reraise=True, stop=stop_after_attempt(3))
def raise_my_exception():
    raise MyException("Fail")


def test_raise_my_exception():
    try:
        raise_my_exception()
    except MyException:
        # timed out retrying
        pass


@retry(stop=stop_after_attempt(3), before=before_log(logger, logging.DEBUG))
def raise_my_exception_1():
    raise MyException("Fail")


@retry(stop=stop_after_attempt(3), after=after_log(logger, logging.DEBUG))
def raise_my_exception_2():
    raise MyException("Fail")


@retry(stop=stop_after_attempt(3), before_sleep=before_sleep_log(logger, logging.DEBUG))
def raise_my_exception_3():
    raise MyException("Fail")


@retry(stop=stop_after_attempt(3))
def raise_my_exception_4():
    raise MyException("Fail")


def test_statistics():
    try:
        raise_my_exception()
    except Exception:
        pass

    print("statistics = ", raise_my_exception.retry.statistics)


def return_last_value(retry_state):
    """return the result of the last call attempt"""
    return retry_state.outcome.result()


def is_false(value):
    """Return True if value is False"""
    return value is False


# will return False after trying 3 times to get a different result
@retry(stop=stop_after_attempt(3), retry_error_callback=return_last_value, retry=retry_if_result(is_false))
def eventually_return_false():
    return False
