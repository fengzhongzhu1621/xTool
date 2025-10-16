from django.db import models
from django.utils.translation import gettext_lazy as _lazy

from core.constants import LEN_LONG, LEN_MIDDLE, LEN_SHORT
from core.models import SoftDeleteModel


class Area(SoftDeleteModel):
    name = models.CharField(max_length=LEN_MIDDLE, verbose_name=_lazy("名称"))
    code = models.CharField(max_length=LEN_SHORT, verbose_name=_lazy("地区编码"), unique=True, db_index=True)
    level = models.BigIntegerField(verbose_name=_lazy("地区层级(1省份 2城市 3区县 4乡级)"))
    pinyin = models.CharField(max_length=LEN_LONG, verbose_name=_lazy("拼音"))
    initials = models.CharField(max_length=LEN_SHORT, verbose_name=_lazy("首字母"))
    enable = models.BooleanField(default=True, verbose_name=_lazy("是否启用"))
    parent_code = models.ForeignKey(
        to="self",
        verbose_name=_lazy("父地区编码"),
        to_field="code",
        on_delete=models.CASCADE,
        db_constraint=False,
        null=True,
        blank=True,
    )

    class Meta:
        verbose_name = _lazy("地区表")
        verbose_name_plural = verbose_name

    def __str__(self):
        return f"{self.name}"
