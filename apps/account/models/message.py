from django.db import models
from django.utils.translation import gettext_lazy as _lazy

from core.constants import LEN_MIDDLE
from core.models import SoftDeleteModel


class MessageCenter(SoftDeleteModel):
    title = models.CharField(max_length=LEN_MIDDLE, verbose_name=_lazy("标题"))
    content = models.TextField(verbose_name=_lazy("内容"))
    target_type = models.IntegerField(default=0, verbose_name=_lazy("目标类型"))
    target_user = models.ManyToManyField(
        to="Users",
        related_name="user",
        through="MessageCenterTargetUser",
        through_fields=("message_center", "users"),
        blank=True,
        verbose_name=_lazy("目标用户"),
    )
    target_dept = models.ManyToManyField(to="Dept", blank=True, db_constraint=False, verbose_name=_lazy("目标部门"))
    target_role = models.ManyToManyField(to="Role", blank=True, db_constraint=False, verbose_name=_lazy("目标角色"))

    class Meta:
        verbose_name = "消息中心"
        verbose_name_plural = verbose_name


class MessageCenterTargetUser(SoftDeleteModel):
    users = models.ForeignKey(
        "Users",
        related_name="target_user",
        on_delete=models.CASCADE,
        db_constraint=False,
        verbose_name=_lazy("关联用户表"),
    )
    message_center = models.ForeignKey(
        MessageCenter,
        on_delete=models.CASCADE,
        db_constraint=False,
        verbose_name=_lazy("关联消息中心表"),
    )
    is_read = models.BooleanField(default=False, blank=True, null=True, verbose_name=_lazy("是否已读"))

    class Meta:
        verbose_name = _lazy("消息中心目标用户表")
        verbose_name_plural = verbose_name
