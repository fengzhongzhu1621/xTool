from typing import Any

from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _lazy

from core.cache import CacheKey
from core.constants import LEN_LONG, TimeEnum
from core.models import OptionBase, SoftDeleteModelManager

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
