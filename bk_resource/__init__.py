from bk_resource.base import Resource
from bk_resource.contrib import APIResource, BkApiResource, CacheResource
from bk_resource.management.root import adapter, api, resource

default_app_config = "bk_resource.apps.BKResourceConfig"

__author__ = "蓝鲸智云"
__copyright__ = "Copyright (c)   2012-2021 Tencent BlueKing. All Rights Reserved."
__doc__ = """
自动发现项目下resource和adapter和api
    cc
    ├── adapter
    │   ├── default.py
    │   ├── community
    │   │   └── resources.py
    │   └── enterprise
    │       └── resources.py
    └── resources.py
    使用:
        resource.cc -> cc/resources.py
        # 调用resource.cc 即可访问对应文件下的resource
        adapter.cc -> cc/adapter/default.py -> cc/adapter/${platform}/resources.py
        # 调用adapter.cc 既可访问对应文件下的resource，
        # 如果在${platform}/resources.py里面有相同定义，会重载default.py下的resource
    """
__all__ = [
    "Resource",
    "CacheResource",
    "APIResource",
    "BkApiResource",
    "adapter",
    "api",
    "resource",
    "contrib",
]
