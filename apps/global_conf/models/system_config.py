from django.db import models
from django.utils.translation import gettext_lazy as _lazy

from core.constants import LEN_SHORT, FormItemType
from core.models import SoftDeleteModel

__all__ = ["SystemConfig"]


class SystemConfig(SoftDeleteModel):
    parent = models.ForeignKey(
        to="self", verbose_name=_lazy("父级"), on_delete=models.CASCADE, db_constraint=False, null=True, blank=True
    )
    title = models.CharField(max_length=50, verbose_name=_lazy("标题"))
    key = models.CharField(max_length=20, verbose_name=_lazy("键"), db_index=True)
    value = models.JSONField(max_length=100, verbose_name=_lazy("值"), null=True, blank=True)
    sort = models.IntegerField(default=0, verbose_name=_lazy("排序"), blank=True)
    status = models.BooleanField(default=True, verbose_name=_lazy("启用状态"))
    data_options = models.JSONField(verbose_name=_lazy("数据options"), null=True, blank=True)
    form_item_type = models.CharField(
        max_length=LEN_SHORT, choices=FormItemType.choices, verbose_name=_lazy("表单类型"), default=0, blank=True
    )
    rule = models.JSONField(null=True, blank=True, verbose_name=_lazy("校验规则"))
    placeholder = models.CharField(max_length=50, null=True, blank=True, verbose_name=_lazy("提示信息"))
    setting = models.JSONField(null=True, blank=True, verbose_name=_lazy("配置"))

    class Meta:
        app_label = "global_conf"
        verbose_name = _lazy("系统配置表")
        verbose_name_plural = verbose_name
        unique_together = (("key", "parent_id"),)

    def __str__(self):
        return f"{self.title}"
