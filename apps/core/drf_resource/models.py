# -*- coding: utf-8 -*-

from typing import List, Union, Dict, Optional

from django.test import RequestFactory

from rest_framework.viewsets import ModelViewSet
from .base import Resource

CREATE = "create"
LIST = "list"
RETRIEVE = "retrieve"
UPDATE = "update"
PARTIAL_UPDATE = "partial_update"

MAPPING = {
    CREATE: "post",
    LIST: "get",
    RETRIEVE: "get",
    UPDATE: "put",
    PARTIAL_UPDATE: "patch",
}


class ModelResource(Resource, ModelViewSet):
    def perform_request(self, validated_request_data: Optional[Dict], *args, **kwargs) -> Union[List, Dict, None]:
        # 创建request对象
        method = self.method if self.method else MAPPING[self.action]
        request = RequestFactory().request(REQUEST_METHOD=method.upper())
        # 设置request对象的请求内容
        method_lower = request.method.lower()
        if method_lower in ["get"]:
            setattr(request, "query_params", validated_request_data)
        elif method_lower in ["post", "put", "patch"]:
            setattr(request, "data", validated_request_data)
        # 创建请求视图
        request_handler = self.__class__.as_view(actions={
            method_lower: self.action
        }, **kwargs)
        # 执行视图方法
        response = request_handler(request, *args, **kwargs)
        return response.data
