from bk_resource import Resource
from django.utils.translation import gettext_lazy as _lazy


class GlobalConfBaseResource(Resource):
    tags = [_lazy("全局配置")]
