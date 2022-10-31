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
        init_kwargs = {}
        request_handler_kwargs = {}
        # 创建request对象
        action = kwargs["action"]
        if action not in MAPPING:
            action_func = getattr(self, action, None)
            detail = action_func.detail
            for key, value in action_func.mapping.items():
                if value == action:
                    method = key
        else:
            if action in [RETRIEVE, UPDATE, PARTIAL_UPDATE]:
                detail = True
            else:
                detail = False
            method = MAPPING[action]
        if detail:
            request_handler_kwargs["pk"] = validated_request_data["id"]
        # 构造请求
        request = RequestFactory().request(REQUEST_METHOD=method.upper())
        # 设置request对象的请求内容
        method_lower = request.method.lower()
        if method_lower in ["get"]:
            setattr(request, "query_params", validated_request_data)
        elif method_lower in ["post", "put", "patch"]:
            setattr(request, "data", validated_request_data)
        # 创建请求视图
        request_handler = self.__class__.as_view(actions={
            method_lower: action
        }, **init_kwargs)
        # 执行视图方法

        response = request_handler(request, **request_handler_kwargs)
        return response.data
