from django.utils.translation import gettext_lazy as _lazy

TABLE = "TABLE"
BASE_MODEL = "BASE-MODEL"

REGEX_MATCHES_ERROR_MESSAGE_FOR_KEY = _lazy("仅支持英文字符、数字及下划线的组合，不允许以下划线开头或结尾")

# crontab 的格式
CRON_REPR = """\
{0._orig_minute} {0._orig_hour} {0._orig_day_of_week} \
{0._orig_day_of_month} {0._orig_month_of_year}\
"""
