from django.db.models import TextChoices
from django.utils.translation import gettext_lazy as _lazy


class PeriodicTaskType(TextChoices):
    REMOTE = "remote", _lazy("远程 API 周期任务")
    LOCAL = "local", _lazy("本地函数周期任务")
