import abc

from bk_resource import Resource
from django.utils.translation import gettext_lazy as _lazy


class HttpClientBaseResource(Resource, abc.ABC):
    tags = [_lazy("HTTP 请求")]
