from collections import OrderedDict

from django.conf import settings
from django.utils.translation import gettext as _
from rest_framework.exceptions import ValidationError
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class CustomPageNumberPagination(PageNumberPagination):
    """
    自定义分页
    """

    # 默认一页拉取的数量
    page_size = 100

    # 获取URL参数中传入的页码key字段
    page_query_param = "page"

    # 指定单页最大值的字段
    page_size_query_param = "page_size"

    # 设置单次拉取的最大值
    max_page_size = 1000

    def get_paginated_response(self, data):
        """
        返回分页后的Response
        """
        return Response(
            OrderedDict(
                [
                    ("page", self.page.number),
                    ("num_pages", self.page.paginator.num_pages),
                    ("total", self.page.paginator.count),
                    ("results", data),
                ]
            )
        )

    def get_paginated_data(self, data):
        """
        生成分页数据
        """
        return OrderedDict(
            [
                ("page", self.page.number),
                ("num_pages", self.page.paginator.num_pages),
                ("total", self.page.paginator.count),
                ("results", data),
            ]
        )


class CustomPageNumberWithColumnPagination(CustomPageNumberPagination):
    """自定义分页器，支持返回表格的表头元数据 ."""

    def __init__(self):
        super().__init__()
        self.columns = []

    def paginate_queryset(self, queryset, request, view):
        """
        返回分页查询数据
        部分列表接口要求一次返回所有数据,此类接口不做数据量限制
        """
        page_size = request.query_params.get(self.page_size_query_param, None)
        if page_size is not None:
            page_size = int(page_size)
            if page_size > settings.MAX_PAGE_SIZE:
                raise ValidationError(_("分页查询数量超过限制的最大值, 建议值{}").format(settings.MAX_PAGE_SIZE))
            if page_size <= 0:
                raise ValidationError(_("分页查询数量不能小于等于0"))
        if isinstance(queryset, dict):
            data = queryset["data"]
            self.columns = queryset["columns"]
        else:
            data = queryset
        return super().paginate_queryset(data, request, view)

    def get_paginated_response(self, data):
        """
        返回分页后的Response
        """
        return Response(self.get_paginated_data(data))

    def get_paginated_data(self, data):
        """
        生成分页数据
        """
        value = super().get_paginated_data(data)
        if self.columns:
            value.append(("columns", self.columns))
        return OrderedDict(value)


class CustomLimitOffsetPagination(LimitOffsetPagination):
    """自定义limitoffset分页器 ."""

    def get_paginated_response(self, data):
        return Response(
            OrderedDict(
                [
                    ("count", self.count),
                    ("results", data),
                ]
            )
        )
