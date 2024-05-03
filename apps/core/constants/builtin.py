# -*- coding: utf-8 -*-

from django.utils.translation import gettext_lazy as _lazy

from xTool.algorithms.collections import ConstantDict

LEN_SHORT = 32
LEN_NORMAL = 64
LEN_MIDDLE = 128
LEN_LONG = 255
LEN_X_LONG = 1000
LEN_XX_LONG = 10000
LEN_XXX_LONG = 20000

EMPTY_INT = 0
EMPTY_STRING = ""
EMPTY_LIST = []
EMPTY_DICT = ConstantDict({})
EMPTY_VARIABLE = {"inputs": [], "outputs": []}
DEFAULT_BK_BIZ_ID = -1
EMPTY = "EMPTY"

TABLE = "TABLE"
BASE_MODEL = "BASE-MODEL"

# 统一各处ID及简称、名称的校验规范
REGEX_MATCHES_ERROR_MESSAGE_FOR_KEY = _lazy("仅支持英文字符、数字及下划线的组合，不允许以下划线开头或结尾")
REGEX_FOR_KEY = "^(?!_)(?!.*?_$)[A-Za-z0-9_]+$"

# crontab 的格式
CRON_REPR = """\
{0._orig_minute} {0._orig_hour} {0._orig_day_of_week} \
{0._orig_day_of_month} {0._orig_month_of_year}\
"""
