from rest_framework.routers import DefaultRouter
from rest_framework.viewsets import GenericViewSet

from bk_resource.tools import get_underscore_viewset_name
from bk_resource.viewsets import ResourceViewSet


class ResourceRouter(DefaultRouter):
    @staticmethod
    def _init_resource_viewset(viewset):
        """
        初始化ResourceViewset，动态增加方法，在register router前必须进行调用
        @:param viewset: ResourceViewset类
        """
        if isinstance(viewset, type) and issubclass(viewset, ResourceViewSet):
            viewset.generate_endpoint()

    def register(self, prefix, viewset, base_name=None):
        """
        注册单个ResourceViewset
        """
        self._init_resource_viewset(viewset)
        super().register(prefix, viewset, base_name)

    def register_module(self, viewset_module, prefix=None):
        """
        注册整个ResourceViewset模块，并根据类的命名规则自动生成对应的url
        """
        items = viewset_module.__dict__.items()
        for attr, viewset in items:
            # 全小写的属性不是类，忽略
            if attr.startswith("_") or attr[0].islower():
                continue
            # 忽略 ResourceViewSet
            if attr == "ResourceViewSet":
                continue
            if isinstance(viewset, type) and issubclass(viewset, GenericViewSet):
                module_prefix = self.get_default_basename(viewset)
                if prefix:
                    module_prefix = f"{prefix}/{module_prefix}" if module_prefix else prefix
                self.register(module_prefix, viewset)

    def get_default_basename(self, viewset: ResourceViewSet):
        return get_underscore_viewset_name(viewset)
