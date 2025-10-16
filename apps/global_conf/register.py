from typing import Any, Dict, List, Optional

from django.db import ProgrammingError

from .models import GlobalConfig, GlobalConfigCacheKey


class GlobalConfigItem:
    def __init__(
        self,
        value: Any,
        description: Optional[str],
        name: Optional[str] = None,
    ) -> None:
        self.name = name
        self.value = value
        self.description = description if description is not None else ""

    def set_name(self, name: str) -> "GlobalConfigItem":
        self.name = name
        return self

    def __str__(self) -> str:
        return self.name


_global_configs: Dict[str, GlobalConfigItem] = {}


def register_global_config(cls):
    """注册全局配置，将配置默认值写入到数据库 ."""
    global _global_configs
    config_items = {
        name: config_item.set_name(name)
        for name, config_item in cls.__dict__.items()
        if isinstance(config_item, GlobalConfigItem)
    }
    _global_configs.update(config_items)
    try:
        init_or_update_global_config(list(config_items.values()))
    except (RuntimeError, ProgrammingError):
        pass

    return cls


def list_registered_configs() -> Dict[str, GlobalConfigItem]:
    return _global_configs


def init_or_update_global_config(config_items: List[GlobalConfigItem]) -> None:
    """初始化全局配置"""
    for config_item in config_items:
        if not config_item.name:
            continue
        # 初始化配置到数据库
        new_model = GlobalConfig.create_option(config_item.value)
        value = new_model.value
        value_type = new_model.value_type
        name = config_item.name
        instance, is_created = GlobalConfig.objects.get_or_create(
            name=name,
            defaults={
                "value": value,
                "value_type": value_type,
                "description": config_item.description,
            },
        )
        if is_created:
            # 刷新缓存
            cache = GlobalConfigCacheKey(name=name)
            cache.set(value)
            continue

        # 更新部分字段
        update_fields = []
        if instance.description != config_item.description:
            instance.description == config_item.description
            update_fields.append("description")

        if instance.value_type != config_item.value_type.value:
            instance.value_type == config_item.value_type.value
            update_fields.append("value_type")

        if update_fields:
            instance.save(update_fields=update_fields)
