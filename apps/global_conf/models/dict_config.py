from django.db import models
from django.utils.translation import gettext_lazy as _lazy

from core.constants import LEN_LONG, LEN_MIDDLE, LEN_SHORT, FieldType
from core.models import SoftDeleteModel

__all__ = ["Dictionary"]


class Dictionary(SoftDeleteModel):
    label = models.CharField(max_length=LEN_MIDDLE, blank=True, null=True, verbose_name=_lazy("字典名称"))
    value = models.CharField(max_length=LEN_LONG, blank=True, null=True, verbose_name=_lazy("字典编号"))
    parent = models.ForeignKey(
        to="self",
        related_name="sublist",
        db_constraint=False,
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        verbose_name=_lazy("父级"),
    )
    type = models.CharField(
        choices=FieldType.choices, max_length=LEN_SHORT, default=FieldType.TEXT.value, verbose_name=_lazy("数据值类型")
    )
    color = models.CharField(max_length=LEN_SHORT, blank=True, null=True, verbose_name=_lazy("颜色"))
    is_value = models.BooleanField(default=False, verbose_name=_lazy("是否为value值"))
    status = models.BooleanField(default=True, verbose_name=_lazy("状态"))
    sort = models.IntegerField(default=1, verbose_name=_lazy("显示排序"), null=True, blank=True)
    remark = models.TextField(verbose_name=_lazy("备注"), default="")

    class Meta:
        app_label = "global_conf"
        verbose_name = _lazy("字典表")
        verbose_name_plural = verbose_name
