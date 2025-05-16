import threading
import time

import pytest

from xTool.collections.flowctrl import (
    BoundedEmptySemaphore,
    GlobalThrottle,
    LocalThrottle,
    throttle,
)


class TestBoundedEmptySemaphore:
    def test_semaphore(self):
        max_unused = 2
        semaphore = BoundedEmptySemaphore(max_unused)
        semaphore.release()
        semaphore.release()
        with pytest.raises(ValueError):
            semaphore.release()


def test_GlobalThrottle():
    @GlobalThrottle(1, 2)
    def f():
        pass

    time.sleep(1)
    begin_time = time.time()
    t_list = []
    for _ in range(5):
        t = threading.Thread(target=f)
        t.start()
        t_list.append(t)
    for t in t_list:
        t.join()
    end_time = time.time()
    duration = end_time - begin_time
    assert duration >= 4 and duration < 5


def test_LocalThrottle():
    def f():
        @LocalThrottle(1)
        def f1():
            pass

        f1()
        f1()
        f1()

    begin_time = time.time()
    t = threading.Thread(target=f)
    t.start()
    t.join()
    end_time = time.time()
    duration = end_time - begin_time
    assert duration >= 2 and duration < 3


def test_throttle():
    start = time.time()
    with throttle(1):
        pass
    assert 1 <= time.time() - start <= 1.1

    @throttle(1)
    def f():
        pass

    start = time.time()
    f()
    assert 1 <= time.time() - start <= 1.1

    start = time.time()
    with throttle(1):
        time.sleep(2)
    assert 2 <= time.time() - start <= 2.1

    @throttle(1)
    def f():
        time.sleep(2)

    start = time.time()
    f()
    assert 2 <= time.time() - start <= 2.1

    start = time.time()

    try:
        with throttle(1):
            raise ValueError("foo")
    except ValueError:
        end = time.time()
    assert 0 <= end - start <= 0.1

    @throttle(1)
    def f():
        raise ValueError("foo")

    start = time.time()
    try:
        f()
    except ValueError:
        end = time.time()

    assert 0 <= end - start <= 0.1
