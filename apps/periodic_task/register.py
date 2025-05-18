from celery import shared_task

from apps.periodic_task.constants import PeriodicTaskType
from apps.periodic_task.models import MultiTypePeriodicTask

__registered_local_tasks = set()


def register_periodic_task(run_every, args=None, kwargs=None):
    """
    注册周期任务
    """

    def inner_wrapper(wrapped_func):
        name = f"{wrapped_func.__module__}.{wrapped_func.__name__}"
        __registered_local_tasks.add(name)

        MultiTypePeriodicTask.objects.create_or_update_periodic_task(
            name=name, task=name, task_type=PeriodicTaskType.LOCAL.value, run_every=run_every, args=args, kwargs=kwargs
        )
        return shared_task(wrapped_func)

    return inner_wrapper
