import abc

from django.utils.translation import gettext_lazy as _lazy

from bk_resource import Resource


class HttpClientBaseResource(Resource, abc.ABC):
    tags = [_lazy("HTTP 请求")]
