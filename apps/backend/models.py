from django.db import models
from django.db.models import QuerySet
from django.utils import timezone
from django.utils.translation import gettext_lazy as _lazy

from core.constants import LEN_MIDDLE, LEN_SHORT


class DataManager(models.Manager):
    def get_queryset(self):
        return QuerySet(self.model).exclude(expire_at__lte=timezone.now())


class Data(models.Model):
    """数据存储"""

    TYPE_CHOICES = (
        ("string", _lazy("字符串")),
        ("hash", _lazy("哈希值")),
        ("list", _lazy("列表")),
        ("set", _lazy("集合")),
        ("zset", _lazy("有序集合")),
    )
    key = models.CharField(_lazy("关键字"), max_length=LEN_MIDDLE, db_index=True)
    value = models.IntegerField(verbose_name=_lazy("值"))
    type = models.CharField(_lazy("类型"), choices=TYPE_CHOICES, default="string", max_length=LEN_SHORT)
    expire_at = models.DateTimeField(_lazy("过期时间"), null=True, blank=True, db_index=True)

    objects = DataManager()

    class Meta:
        app_label = "backend"
        verbose_name = _lazy("数据存储")
        verbose_name_plural = _lazy("数据存储")

    def __str__(self):
        return "{}({})".format(self.key, self.type)
