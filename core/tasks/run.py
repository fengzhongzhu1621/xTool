import time
from typing import Callable

from apps.logger import logger
from core.lock import share_lock


def run_sub_task(task_name: str, wrapper: Callable, identify: str, *args, **kwargs):
    """执行子任务 ."""
    start = time.time()
    try:
        logger.info("^[Cron Task](%s %s) start", task_name, identify)
        result = share_lock(identify=identify)(wrapper)(*args, **kwargs)
    except Exception as exc_info:  # noqa
        logger.exception("![Cron Task](%s %s) error: %s", task_name, identify, exc_info)
        raise
    finally:
        time_cost = time.time() - start
        logger.info("$[Cron Task](%s %s) cost: %s", task_name, identify, time_cost)

    return result
