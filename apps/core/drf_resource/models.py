# -*- coding: utf-8 -*-

from enum import Enum, unique
from typing import List, Union, Dict, Optional

from django.test import RequestFactory

from rest_framework.viewsets import ModelViewSet
from .base import Resource


@unique
class Action(Enum):
    CREATE = "create"
    LIST = "list"
    RETRIEVE = "retrieve"
    UPDATE = "update"
    PARTIAL_UPDATE = "partial_update"


MAPPING = {
    Action.CREATE: "post",
    Action.LIST: "get",
    Action.RETRIEVE: "get",
    Action.UPDATE: "put",
    Action.PARTIAL_UPDATE: "patch",
}


class ModelResource(Resource, ModelViewSet):
    def perform_request(self, validated_request_data: Optional[Dict], *args, **kwargs) -> Union[List, Dict, None]:
        # 创建request对象
        method = MAPPING[self.action]
        request = RequestFactory().request(REQUEST_METHOD=method.upper())
        # 设置request对象的请求内容
        if request.method.lower() in ["get"]:
            setattr(request, "query_params", validated_request_data)
        elif request.method.lower() in ["post", "put", "patch"]:
            setattr(request, "data", validated_request_data)
        # 创建请求视图
        request_handler = self.__class__.as_view(actions={
            method: self.action.value
        }, **kwargs)
        # 执行视图方法
        response = request_handler(request, *args, **kwargs)
        return response.data
