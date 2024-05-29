from django.db.models import TextChoices
from django.utils.translation import gettext_lazy as _lazy


class Gender(TextChoices):
    """性别 ."""

    UNKNOWN = "UNKNOWN", _lazy("未知")
    MALE = "MALE", _lazy("男")
    FEMALE = "FEMALE", _lazy("女")


class UserType(TextChoices):
    """用户类型 ."""

    BACKEND = "BACKEND", _lazy("后台用户")
    FRONTEND = "FRONTEND", _lazy("前台用户")


class PostStatus(TextChoices):
    """职位状态 ."""

    QUIT = "QUIT", _lazy("离职")
    IN_SERVICE = "IN_SERVICE", _lazy("在职")


class DataScope(TextChoices):
    USER = "USER", _lazy("仅本人数据权限")
    GROUP = "GROUP", _lazy("本部门及以下数据权限")
    DEPT = "DEPT", _lazy("本部门数据权限")
    ALL = "ALL", _lazy("全部数据权限")
    CUSTOM = "CUSTOM", _lazy("自定数据权限")
