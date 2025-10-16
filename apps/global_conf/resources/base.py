from django.utils.translation import gettext_lazy as _lazy

from bk_resource import Resource


class GlobalConfBaseResource(Resource):
    tags = [_lazy("全局配置")]
