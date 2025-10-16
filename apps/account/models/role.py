from django.db import models
from django.utils.translation import gettext_lazy as _lazy

from core.constants import LEN_NORMAL, LEN_SHORT, DataScope
from core.models import SoftDeleteModel


class Role(SoftDeleteModel):
    name = models.CharField(max_length=LEN_NORMAL, verbose_name=_lazy("角色名称"))
    key = models.CharField(max_length=LEN_NORMAL, unique=True, verbose_name=_lazy("权限字符"))
    sort = models.IntegerField(default=1, verbose_name=_lazy("角色顺序"))
    status = models.BooleanField(default=True, verbose_name=_lazy("角色状态"))

    class Meta:
        app_label = "account"
        verbose_name = _lazy("角色表")
        verbose_name_plural = verbose_name


class FieldPermission(SoftDeleteModel):
    role = models.ForeignKey(to="Role", on_delete=models.CASCADE, verbose_name=_lazy("角色"), db_constraint=False)
    field = models.ForeignKey(
        to="MenuField",
        on_delete=models.CASCADE,
        related_name="menu_field",
        verbose_name=_lazy("字段"),
        db_constraint=False,
    )
    is_query = models.BooleanField(default=1, verbose_name=_lazy("是否可查询"))
    is_create = models.BooleanField(default=1, verbose_name=_lazy("是否可创建"))
    is_update = models.BooleanField(default=1, verbose_name=_lazy("是否可更新"))

    class Meta:
        verbose_name = _lazy("字段权限表")
        verbose_name_plural = verbose_name


class RoleMenuPermission(SoftDeleteModel):
    role = models.ForeignKey(
        to="Role",
        db_constraint=False,
        related_name="role_menu",
        on_delete=models.CASCADE,
        verbose_name=_lazy("关联角色"),
    )
    menu = models.ForeignKey(
        to="Menu",
        db_constraint=False,
        related_name="role_menu",
        on_delete=models.CASCADE,
        verbose_name=_lazy("关联菜单"),
    )

    class Meta:
        verbose_name = _lazy("角色菜单权限表")
        verbose_name_plural = verbose_name


class RoleMenuButtonPermission(SoftDeleteModel):
    role = models.ForeignKey(
        to="Role",
        db_constraint=False,
        related_name="role_menu_button",
        on_delete=models.CASCADE,
        verbose_name=_lazy("关联角色"),
    )
    menu_button = models.ForeignKey(
        to="MenuButton",
        db_constraint=False,
        related_name="menu_button_permission",
        on_delete=models.CASCADE,
        verbose_name=_lazy("关联菜单按钮"),
        null=True,
        blank=True,
    )
    data_range = models.CharField(
        max_length=LEN_SHORT,
        default=DataScope.USER.value,
        choices=DataScope.choices,
        verbose_name=_lazy("数据权限范围"),
    )
    dept = models.ManyToManyField(to="Dept", blank=True, verbose_name=_lazy("数据权限-关联部门"), db_constraint=False)

    class Meta:
        verbose_name = _lazy("角色按钮权限表")
        verbose_name_plural = verbose_name
