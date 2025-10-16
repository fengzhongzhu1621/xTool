import json
from typing import List

from django.db import models, transaction
from django.utils.translation import gettext_lazy as _lazy
from django_celery_beat.models import PeriodicTask
from django_celery_beat.schedulers import ModelEntry

from apps.periodic_task.constants import PeriodicTaskType
from core.constants import LEN_LONG, LEN_SHORT
from core.models import OperateRecordModel, OperateRecordModelManager


class MultiTypePeriodicTaskManager(OperateRecordModelManager):
    def create_or_update_periodic_task(self, name: str, task, run_every, task_type, args=None, kwargs=None):
        """
        创建或更新周期性任务（Periodic Task）。

        name：任务名称（唯一）。
        task：Celery 任务名称（如 "my_app.tasks.my_task"）。
        run_every：执行周期（如 crontab(minute='*/5') 或 timedelta(minutes=5)）。
        task_type：任务类型（如 "data_sync"）。
        args、kwargs：任务参数（可选，默认为空列表/字典）。
        """
        # 转换执行周期，将 run_every 转换为 Celery 可识别的格式（如 crontab 或 timedelta），
        # 并返回 model_schedule 和 model_field（如 "crontab" 或 "interval"）
        model_schedule, model_field = ModelEntry.to_model_schedule(run_every)
        # 转换执行参数
        _args = json.dumps(args or [])
        _kwargs = json.dumps(kwargs or {})

        try:
            db_task = self.get(name=name)
        except self.model.DoesNotExist:
            # 新建周期任务
            celery_task = PeriodicTask.objects.create(
                name=name, task=task, args=_args, kwargs=_kwargs, **{model_field: model_schedule}
            )
            self.create(name=name, task=celery_task, task_type=task_type)
        else:
            # 周期任务已存在且未冻结的情况，需要更新执行周期和执行参数
            if not db_task.is_frozen:
                celery_task = db_task.task
                # 修改 crontab 配置
                setattr(celery_task, model_field, model_schedule)
                celery_task.args = _args
                celery_task.kwargs = _kwargs
                celery_task.save(update_fields=[model_field, "args", "kwargs"])

    @transaction.atomic
    def delete_legacy_periodic_tasks(self, task_name_list: List[str], task_type: str):
        """删除周期性任务 ."""
        # 根据任务名称查询需要删除的任务
        legacy_tasks = self.filter(task_type=task_type).exclude(name__in=task_name_list)
        celery_task_ids = list(legacy_tasks.values_list("task_id", flat=True))
        # 删除celery任务
        self.filter(id__in=celery_task_ids).delete()
        legacy_tasks.delete()

    def get_periodic_task_run_every(self, func_name: str):
        """获取定时任务的运行周期"""
        db_task = self.get(name__contains=func_name)
        return db_task.task.crontab.schedule


class MultiTypePeriodicTask(OperateRecordModel):
    name = models.CharField(_lazy("周期任务名称"), max_length=LEN_LONG, unique=True)
    task = models.ForeignKey(
        PeriodicTask, verbose_name=_lazy("celery 周期任务实例"), on_delete=models.CASCADE, db_constraint=False
    )
    task_type = models.CharField(_lazy("任务类型"), choices=PeriodicTaskType.choices, max_length=LEN_SHORT)
    is_frozen = models.BooleanField(_lazy("是否冻结"), default=False)

    class Meta:
        verbose_name_plural = verbose_name = _lazy("周期任务")

    def __str__(self):
        return self.name
