from django.db.models import TextChoices
from django.utils.translation import gettext_lazy as _lazy


class NoticeSignalEnum(TextChoices):
    recovered = "recovered", _lazy("告警恢复时")
    abnormal = "abnormal", _lazy("告警触发时")
    closed = "closed", _lazy("告警关闭时")
    ack = "ack", _lazy("告警确认时")
    no_data = "no_data", _lazy("无数据告警")
