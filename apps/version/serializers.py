from django.utils.translation import gettext as _
from rest_framework import serializers

from core.constants import LEN_SHORT


class VersionLogDetailRequestSerializer(serializers.Serializer):
    log_version = serializers.CharField(label=_("版本号"), max_length=LEN_SHORT)
