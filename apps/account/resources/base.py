import abc

from django.utils.translation import gettext_lazy as _lazy

from bk_resource import Resource
from core.models import ModelResourceMixin


class UserBaseResource(ModelResourceMixin, Resource, abc.ABC):
    tags = [_lazy("用户")]
