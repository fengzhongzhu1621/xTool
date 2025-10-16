from prometheus_client.utils import INF

from .counter import Counter
from .histogram import Histogram


class StatusEnum:
    """
    任务状态枚举
    """

    SUCCESS = "success"
    FAILED = "failed"

    @classmethod
    def from_exc(cls, expr):
        return cls.FAILED if expr else cls.SUCCES


CELERY_TASK_EXECUTE_TIME = Histogram(
    name="celery_task_execute_time",
    documentation="celery 任务执行耗时",
    labelnames=(
        "task_name",
        "queue",
        "exception",
    ),
    buckets=(0.1, 0.5, 1, 3, 5, 10, 30, 60, 300, 1800, INF),
)

CRON_TASK_EXECUTE_COUNT = Counter(
    name="cron_task_execute_count",
    documentation="周期任务执行次数",
    labelnames=(
        "task_name",
        "queue",
        "status",
        "exception",
    ),
)
