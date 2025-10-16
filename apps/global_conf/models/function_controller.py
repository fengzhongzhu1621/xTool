from django.conf import settings
from django.core.cache import cache
from django.db import models, transaction
from django.utils.translation import gettext_lazy as _lazy
from mptt.managers import TreeManager
from mptt.models import MPTTModel, TreeForeignKey

from core.constants import LEN_LONG

__all__ = [
    "FunctionController",
]


class FunctionController(MPTTModel):
    """
    功能开启控制器（基于MPTT树形结构）
    功能开关管理，支持父子层级关系
    """

    name = models.CharField(_lazy("功能名称"), max_length=LEN_LONG, unique=True)
    is_enabled = models.BooleanField(_lazy("是否开启"), default=False)
    is_frozen = models.BooleanField(_lazy("是否冻结"), help_text=_lazy("人工冻结此开关，将不受更新影响"), default=False)

    # MPTT字段
    parent = TreeForeignKey(
        'self', on_delete=models.CASCADE, null=True, blank=True, related_name='children', verbose_name=_lazy("父功能")
    )

    objects = TreeManager()  # 使用MPTT管理器

    class MPTTMeta:
        order_insertion_by = ['name']  # 按名称排序插入

    class Meta:
        app_label = "global_conf"
        verbose_name = verbose_name_plural = _lazy("功能控制器(FunctionController)")

    def __str__(self):
        status = "✅" if self.is_enabled else "❌"
        frozen = "🔒" if self.is_frozen else ""
        return f"{frozen}{self.name} [{status}]"

    @classmethod
    def init_function_controller(cls, function_data=None):
        """
        初始化功能开关（基于MPTT结构）
        :param function_data: 初始化数据，默认从配置加载
        """
        # 获得开关配置
        if function_data is None:
            function_data = settings.FUNCTION_CONTROLLER_INIT_MAP

        with transaction.atomic():
            # 先删除所有现有数据（谨慎操作，生产环境应考虑增量更新）
            cls.objects.all().delete()

            # 批量创建节点
            nodes_to_create = []
            for parent_name, node_data in function_data.items():
                nodes_to_create.extend(cls._build_tree_nodes(parent_name, node_data))

            if nodes_to_create:
                cls.objects.bulk_create(nodes_to_create)

            # 重建MPTT树结构
            cls.objects.rebuild()

    @classmethod
    def _build_tree_nodes(cls, parent_name, node_data):
        """
        递归构建树节点
        """
        nodes = []
        for func_name, func_config in node_data.items():
            current_name = func_config.get("name", func_name)
            is_enabled = func_config.get("is_enabled", False)

            node = cls(
                name=current_name,
                is_enabled=is_enabled,
                is_frozen=func_config.get("is_frozen", False),
                parent=None if parent_name is None else cls.objects.filter(name=parent_name).first(),
            )

            nodes.append(node)

            if "children" in func_config:
                for child in cls._build_tree_nodes(current_name, func_config["children"]):
                    nodes.append(child)

        return nodes

    @classmethod
    def get_all_function_controllers(cls, parent_name: str = None, use_cache=True):
        """
        获取所有功能控制器（带缓存）
        :param parent_name: 父功能名称
        :param use_cache: 是否使用缓存
        :return: 嵌套字典结构的功能数据
        """
        cache_key = f"function_controllers:{parent_name or 'root'}"

        if use_cache:
            cached_data = cache.get(cache_key)
            if cached_data:
                return cached_data

        # 查询根节点或指定父节点的子节点
        if parent_name:
            try:
                parent_node = cls.objects.get(name=parent_name)
                nodes = parent_node.get_children()
            except cls.DoesNotExist:
                nodes = cls.objects.none()
        else:
            nodes = cls.objects.root_nodes()  # 获取所有根节点

        result = {}
        for node in nodes:
            # 检查父节点状态（如果父节点被冻结，则子节点自动冻结）
            if node.parent and node.parent.is_frozen:
                is_enabled = False
                is_frozen = True
            else:
                is_enabled = node.is_enabled and not node.is_frozen
                is_frozen = node.is_frozen

            children = cls.get_all_function_controllers(parent_name=node.name, use_cache=use_cache)

            result[node.name] = {"is_enabled": is_enabled, "is_frozen": is_frozen, "children": children}

        if use_cache:
            cache.set(cache_key, result, timeout=3600)  # 缓存1小时

        return result

    @classmethod
    def get_function_status(cls, name: str) -> bool:
        """
        获取功能状态（自动处理父子关系）
        :param name: 功能名称
        :return: 是否启用（True/False）
        """
        try:
            node = cls.objects.get(name=name)

            # 检查父节点状态
            if node.parent:
                if node.parent.is_frozen:
                    return False
                parent_enabled = cls.get_function_status(node.parent.name)
                if not parent_enabled:
                    return False

            return node.is_enabled and not node.is_frozen
        except cls.DoesNotExist:
            return False

    @classmethod
    def refresh_cache(cls):
        """刷新所有缓存"""
        cache.delete_pattern("function_controllers:*")

    @classmethod
    def batch_update_status(cls, name_list, is_enabled):
        """
        批量更新功能状态
        :param name_list: 功能名称列表
        :param is_enabled: 要设置的状态
        """
        with transaction.atomic():
            nodes = cls.objects.filter(name__in=name_list)
            for node in nodes:
                # 如果父节点被冻结，则不允许修改
                if node.parent and node.parent.is_frozen:
                    continue

                node.is_enabled = is_enabled
                node.save()

            # 更新缓存
            cls.refresh_cache()
