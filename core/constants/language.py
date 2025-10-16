from django.db.models import TextChoices
from django.utils.translation import gettext_lazy as _lazy


class Language(TextChoices):
    ZH_CN = "zh-cn", _lazy("ZH-CN")
    EN = "en", _lazy("EN")


# 不同语言的正则匹配模式
LANGUAGE_REGEX_MAP = {Language.ZH_CN.value: r"[\u4e00-\u9fff]", Language.EN.value: r"[a-zA-Z]"}
