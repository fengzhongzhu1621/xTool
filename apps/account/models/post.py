from django.db import models
from django.utils.translation import gettext_lazy as _lazy

from core.constants import LEN_NORMAL, LEN_SHORT, PostStatus
from core.models import SoftDeleteModel


class Post(SoftDeleteModel):
    name = models.CharField(null=False, max_length=LEN_NORMAL, verbose_name=_lazy("岗位名称"))
    code = models.CharField(max_length=LEN_SHORT, verbose_name=_lazy("岗位编码"))
    sort = models.IntegerField(default=1, verbose_name=_lazy("岗位顺序"))
    status = models.CharField(
        max_length=LEN_SHORT, choices=PostStatus.choices, default=PostStatus.IN_SERVICE, verbose_name=_lazy("岗位状态")
    )

    class Meta:
        app_label = "account"
        verbose_name = _lazy("岗位表")
        verbose_name_plural = verbose_name
