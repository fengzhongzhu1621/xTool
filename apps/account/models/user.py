from django.contrib.auth.models import AbstractUser, UserManager
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _lazy

from apps.account.models import Role
from core.constants import LEN_LONG, LEN_NORMAL, LEN_SHORT, Gender, UserType
from core.models import SoftDeleteModel, SoftDeleteModelManager
from xTool.codec import md5


class CustomUserManager(SoftDeleteModelManager, UserManager):
    def create_superuser(self, username: str, email=None, password=None, **extra_fields):
        user = super().create_superuser(username, email, password, **extra_fields)
        user.set_password(password)
        try:
            user.role.add(Role.objects.get(key="admin"))
            user.save(using=self._db)
            return user
        except ObjectDoesNotExist:
            user.delete()
            raise ValidationError(_lazy("角色`管理员`不存在, 创建失败, 请先执行 python manage.py init"))


class Users(SoftDeleteModel, AbstractUser):
    username = models.CharField(max_length=LEN_NORMAL, unique=True, db_index=True, verbose_name=_lazy("用户账号"))
    email = models.EmailField(max_length=LEN_LONG, verbose_name=_lazy("邮箱"), null=True, blank=True)
    mobile = models.CharField(max_length=LEN_LONG, verbose_name=_lazy("电话"), null=True, blank=True)
    avatar = models.CharField(max_length=LEN_LONG, verbose_name=_lazy("头像"), null=True, blank=True)
    name = models.CharField(max_length=LEN_NORMAL, verbose_name=_lazy("姓名"))

    gender = models.CharField(
        max_length=LEN_SHORT,
        choices=Gender.choices,
        default=Gender.UNKNOWN.value,
        verbose_name=_lazy("性别"),
        null=True,
        blank=True,
    )
    user_type = models.CharField(
        max_length=LEN_SHORT,
        choices=UserType.choices,
        default=UserType.BACKEND.value,
        verbose_name=_lazy("用户类型"),
        null=True,
        blank=True,
    )
    post = models.ManyToManyField(to="Post", blank=True, verbose_name=_lazy("关联岗位"), db_constraint=False)
    role = models.ManyToManyField(to="Role", blank=True, verbose_name=_lazy("关联角色"), db_constraint=False)
    dept = models.ForeignKey(
        to="Dept", verbose_name=_lazy("所属部门"), on_delete=models.PROTECT, db_constraint=False, null=True, blank=True
    )
    objects = CustomUserManager()

    def set_password(self, raw_password):
        """设置用户密码 ."""
        super().set_password(md5(raw_password))

    class Meta:
        app_label = "account"
        verbose_name = _lazy("用户表")
        verbose_name_plural = verbose_name
