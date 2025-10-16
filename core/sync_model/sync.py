from typing import Dict, List, Optional, Set, Type

from django.db import transaction
from django.db.models import Model

from apps.logger import logger
from core.sync_model.models import get_model_value
from xTool.misc import chunks


def get_unique_field_map(models: List, sync_unique_field: str) -> Dict:
    return {getattr(model, sync_unique_field): model for model in models}


def create_models(
    resource: Type[Model],
    unique_value_created_set: Set,
    new_unique_field_map: Dict,
    chunk_created_size: int,
) -> None:
    if not unique_value_created_set:
        return
    resource_models_created = []
    for unique_value in unique_value_created_set:
        resource_model = new_unique_field_map[unique_value]
        resource_models_created.append(resource_model)
    try:
        resource.objects.bulk_create(resource_models_created, chunk_created_size)
    except Exception as exc_info:
        logger.error(exc_info)


def delete_models(
    resource: Type[Model],
    unique_value_deleted: Set,
    old_unique_field_map: Dict,
    chunk_deleted_size: int,
) -> None:
    if not unique_value_deleted:
        return
    delete_ids = [old_unique_field_map[unique_value].id for unique_value in unique_value_deleted]
    for ids in chunks(delete_ids, chunk_deleted_size):
        resource.objects.filter(id__in=ids).delete()


def update_models(
    unique_value_updated: Set,
    new_unique_field_map: Dict,
    old_unique_field_map: Dict,
    sync_fields: List,
    datetime_fields: Set,
    chunk_updated_size: int,
) -> None:
    if not unique_value_updated:
        return
    unique_value_updated = list(unique_value_updated)
    for unique_value_chunk_updated in chunks(unique_value_updated, chunk_updated_size):
        # 批量更新在一次事务中提交
        with transaction.atomic:
            for unique_value in unique_value_chunk_updated:
                old_resource_model = old_unique_field_map[unique_value]
                new_resource_model = new_unique_field_map[unique_value]
                old_compare_data = [
                    get_model_value(old_resource_model, field, datetime_fields) for field in sync_fields
                ]
                new_compare_data = [
                    get_model_value(new_resource_model, field, datetime_fields) for field in sync_fields
                ]
                # 补齐自增ID
                new_resource_model.id = old_resource_model.id
                if old_compare_data != new_compare_data:
                    # 更新指定字段，防止其他的同步进程覆盖同一个字段
                    new_resource_model.save(update_fields=sync_fields)


def sync_data_to_model(
    resource: Type[Model],
    resource_models: List,
    sync_unique_field: str,
    sync_fields: List,
    sync_filter: Optional[Dict] = None,
    datetime_fields: List = None,
    chunk_created_size: int = 50,
    chunk_updated_size: int = 200,
    chunk_deleted_size: int = 1000,
):
    """同步数据到指定的数据表 ."""
    if datetime_fields:
        datetime_fields = set(datetime_fields)
    else:
        datetime_fields = set()

    # 远程模型实例的唯一键值
    new_unique_field_map = get_unique_field_map(resource_models, sync_unique_field)
    new_unique_field_value_set = set(new_unique_field_map.keys())

    # 本地模型实例的唯一键值
    if not sync_filter:
        history_models = resource.objects.all()
    else:
        history_models = resource.objects.filter(**sync_filter)
    old_unique_field_map = get_unique_field_map(history_models, sync_unique_field)
    old_unique_field_value_set = set(old_unique_field_map.keys())

    # 新增记录
    unique_value_created_set = new_unique_field_value_set - old_unique_field_value_set
    create_models(resource, unique_value_created_set, new_unique_field_map, chunk_created_size)

    # 删除记录
    unique_value_deleted = old_unique_field_value_set - new_unique_field_value_set
    delete_models(resource, unique_value_deleted, old_unique_field_map, chunk_deleted_size)

    # 更新记录
    unique_value_updated = new_unique_field_value_set & old_unique_field_value_set
    update_models(
        unique_value_updated,
        new_unique_field_map,
        old_unique_field_map,
        sync_fields,
        datetime_fields,
        chunk_updated_size,
    )
