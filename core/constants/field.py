from django.db.models import TextChoices
from django.utils.translation import gettext_lazy as _lazy


class FieldType(TextChoices):
    """字段类型 ."""

    TEXT = "TEXT", _lazy("文本")
    NUMBER = "NUMBER", _lazy("数字")
    DATE = "DATE", _lazy("日期")
    TIME = "TIME", _lazy("时间")
    DATETIME = "DATETIME", _lazy("日期时间")
    FILE = "FILE", _lazy("文件")
    IMAGE = "IMAGE", _lazy("图片")


class FormItemType(TextChoices):
    TEXT = "TEXT", _lazy("文本")
    DATETIME = "DATETIME", _lazy("日期时间")
    DATE = "DATE", _lazy("日期")
    TIME = "TIME", _lazy("时间")
    TEXTAREA = "TEXTAREA", _lazy("富文本框")
    SELECT = "SELECT", _lazy("下拉列表")
    CHECKBOX = "CHECKBOX", _lazy("复选框")
    RADIO = "RADIO", _lazy("单选框")
    IMAGE = "IMAGE", _lazy("图片")
    FILE = "FILE", _lazy("文件")
    SWITCH = "SWITCH", _lazy("开关")
    NUMBER = "NUMBER", _lazy("数字选择框")
    ARRAY = "ARRAY", _lazy("ARRAY")
    IMAGES = "IMAGES", _lazy("多个图片")
    FOREIGNKEY = "FOREIGNKEY", _lazy("外键-多对一")
    MANYTOMANY = "MANYTOMANY", _lazy("外键-多对多")
