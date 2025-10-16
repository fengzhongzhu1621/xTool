from typing import Dict, Optional

import arrow
from django.db import models
from django.utils.translation import gettext_lazy as _lazy

from core.cache import CacheKey
from core.constants import (
    EMPTY_STRING,
    LEN_MIDDLE,
    LEN_SHORT,
    LEN_X_LONG,
    TimeEnum,
)
from core.models import SoftDeleteModel, SoftDeleteModelManager


class CredentialCacheKey(CacheKey):
    key_template = "credential:{id}"


class CredentialManager(SoftDeleteModelManager):
    def read_conf(self, token: str) -> Dict:
        """获取关联的资源配置 ."""
        # 1. fetch from cache
        value = CredentialCacheKey(id=token).get()
        if value is not None:
            return value
        # 2. fetch from db
        try:
            instance = self.get(token=token)
            # 将最新的配置写到缓存中
            value = instance.refresh_cache()
        except self.model.DoesNotExist:
            # 配置不存在
            value = {}

        return value


class Credential(SoftDeleteModel):
    """凭证表 ."""

    name = models.CharField(_lazy("名称"), max_length=LEN_MIDDLE, null=False)
    token = models.CharField(_lazy("token"), max_length=LEN_SHORT, null=False, unique=True)

    begin_time = models.DateTimeField(_lazy("有效期开始时间"))
    end_time = models.DateTimeField(_lazy("有效期结束时间"), null=True)

    desc = models.CharField(_lazy("描述"), max_length=LEN_X_LONG, default=EMPTY_STRING)

    objects = CredentialManager()

    class Meta:
        app_label = "credential"
        verbose_name = _lazy("凭证")
        verbose_name_plural = _lazy("凭证")

    def refresh_cache(self) -> Dict:
        """刷新配置 ."""
        # 有效期开始时间
        begin_time = arrow.get(self.begin_time).format()
        # 有效期结束时间
        end_time: Optional[str] = arrow.get(self.end_time).format() if self.end_time else None
        # 获得关联的资源
        credential_resources = self.credential_set.all()
        resource_value = []
        cache_value = {
            "token": self.token,
            "begin_time": begin_time,
            "end_time": end_time,
            "resources": resource_value,
        }
        for credential_resource in credential_resources:
            item = {
                "resource_type": credential_resource.resource_type,
                "filter_condition": credential_resource.filter_condition,
            }
            resource_value.append(item)
        # 写缓存
        CredentialCacheKey(id=self.token).set(cache_value, TimeEnum.ONE_DAY_SECOND)

        return cache_value

    def save(self, *args, **kwargs):
        """保存时更新缓存 ."""
        super().save(*args, **kwargs)
        self.refresh_cache()


class CredentialResourceManager(SoftDeleteModelManager):
    pass


class CredentialResource(SoftDeleteModel):
    """凭证资源表 ."""

    credential = models.ForeignKey(
        Credential,
        db_constraint=False,
        on_delete=models.CASCADE,
        help_text=_lazy("凭证"),
        related_name="credential_set",
    )
    resource_type = models.CharField(_lazy("资源类型"), max_length=LEN_SHORT)
    filter_condition = models.JSONField(_lazy("关联范围"), default=dict)

    objects = CredentialResourceManager()

    class Meta:
        app_label = "credential"
        verbose_name = _lazy("凭证关联的资源")
        verbose_name_plural = _lazy("凭证关联的资源")

    def refresh_cache(self) -> Dict:
        """刷新缓存 ."""
        return self.credential.refresh_cache()

    def save(self, *args, **kwargs):
        """保存时更新缓存 ."""
        super().save(*args, **kwargs)
        self.refresh_cache()
