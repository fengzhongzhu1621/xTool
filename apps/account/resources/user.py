from django.utils.translation import gettext_lazy as _lazy

from apps.account.models import Users
from apps.account.serializers import RetrieveUserRequestSerializer
from bk_resource.contrib.model import ModelResource

from .base import UserBaseResource

__all__ = ["RetrieveUserResource"]


class RetrieveUserResource(UserBaseResource, ModelResource):
    name = _lazy("查询用户详情")
    model = Users
    action = "retrieve"
    lookup_field = "id"
    serializer_class = RetrieveUserRequestSerializer
