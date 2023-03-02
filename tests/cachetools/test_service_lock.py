# -*- coding: utf-8 -*-

from xTool.lock import share_lock

count = 0


def test_share_lock(cache):
    def _run_task(a: int, *args, **kwargs):
        global count
        count = count + 1
        return count

    run_task = share_lock(cache)(_run_task)
    assert run_task(a=1) == 1
    assert _run_task._cache_key == "share_lock:cachetools.test_service_lock:_run_task"
    assert run_task(a=1) == 2

    run_task = share_lock(cache, identify="task_a")(_run_task)
    assert run_task(a=1) == 3
    assert _run_task._cache_key == "task_a"
    assert run_task(a=1) == 4

    run_task = share_lock(cache, hash_param=True)(_run_task)
    assert run_task(1, 2) == 5
    assert _run_task._cache_key == "85985a7bd912508f89c96f0ff61e15a6"
    assert run_task(1, b=2, c=3) == 6
    assert _run_task._cache_key == "842277fb3d1e4fc8bd6545c0b4208831"
