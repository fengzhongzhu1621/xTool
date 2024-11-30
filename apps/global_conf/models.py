from typing import Any

from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _lazy

from apps.core.constants import FieldType, FormItemType
from core.cache import CacheKey
from core.constants import (
    LEN_LONG,
)
from core.constants import LEN_SHORT, LEN_MIDDLE
from core.constants import TimeEnum
from core.models import OptionBase, SoftDeleteModelManager
from core.models import SoftDeleteModel

# 全局配置缓存时间
GLOBAL_CONFIG_CACHE_TTL = getattr(settings, "GLOBAL_CONFIG_CACHE_TTL", TimeEnum.TEN_MINUTE_SECOND)


class GlobalConfigCacheKey(CacheKey):
    key_template = "global_config:{name}"

    def set(self, value: Any) -> None:
        super().set(value, GLOBAL_CONFIG_CACHE_TTL)


class GlobalConfigManager(SoftDeleteModelManager):

    def get_value(self, name: str, default=None) -> Any:
        """
        获取配置信息
        :param name: 配置key
        :param default: 默认值
        """
        # 从缓存中读取数据
        cache = GlobalConfigCacheKey(name=name)
        cache_value = cache.get()
        if cache_value is not None:
            return cache_value
        # 从数据库获取记录
        instance = self.filter(name=name).first()
        if instance:
            if instance.value_type == self.model.TYPE_NONE:
                return None
            cache_value = instance.to_json()[name]
        else:
            cache_value = default
        # 刷新缓存
        cache.set(cache_value)

        return cache_value

    def set_value(self, name: str, value: Any, description: str = "") -> None:
        """
        设置配置信息
        """
        # 配置不存则在创建
        instance = self.filter(name=name).first()
        new_model = self.model.create_option(value)
        if instance:
            instance.value = new_model.value
            instance.value_type = new_model.value_type
            instance.description = description
            instance.save(update_fields=["description", "value", "value_type"])
        else:
            self.create(name=name, value=new_model.value, value_type=new_model.value_type)
        # 刷新缓存
        if new_model.value_type != self.model.TYPE_NONE:
            cache = GlobalConfigCacheKey(name=name)
            cache.set(value)


class GlobalConfig(OptionBase):
    """动态配置信息"""

    QUERY_NAME = "name"

    name = models.CharField(_lazy("配置key"), max_length=LEN_LONG, unique=True)
    description = models.TextField(_lazy("描述"), default="", blank=True, null=True)

    objects = GlobalConfigManager()

    class Meta:
        app_label = "global_conf"
        verbose_name = _lazy("全局配置信息")
        verbose_name_plural = _lazy("全局配置信息")
        db_table = "global_setting"

    def __str__(self):
        return self.name


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
