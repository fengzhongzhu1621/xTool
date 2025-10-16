import os
import uuid
from datetime import datetime
from importlib import import_module
from typing import Any, Dict, List, Tuple

import orjson as json
from django.apps import apps
from django.conf import settings
from django.core import exceptions
from django.db import models
from django.db.models import TextChoices
from django.db.models.lookups import Exact
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from rest_framework.settings import api_settings

from core.constants import LEN_NORMAL
from core.utils import get_local_request, is_backend


def get_backend_username():
    return os.getenv("BKAPP_PLATFORM_AUTH_ACCESS_USERNAME", "admin")


def get_non_request_username():
    provider = getattr(settings, "NON_REQUEST_USERNAME_PROVIDER", "")
    if provider:
        try:
            module, method = provider.rsplit(".", 1)
            return getattr(import_module(module), method)()
        except ImportError:
            return provider

    return "admin"


def get_request_username():
    operator = None
    try:
        operator = get_local_request().user.username
    except (IndexError, AttributeError):
        if is_backend():
            operator = get_non_request_username()

    return operator


class OperateRecordQuerySet(models.query.QuerySet):
    """
    批量更新时写入更新时间和更新者
    """

    def update(self, **kwargs):
        """
        重写ORM 更新方法
        """
        kwargs["updated_at"] = timezone.now()
        kwargs["updated_by"] = get_request_username()

        return super().update(**kwargs)


class OperateRecordModelManager(models.Manager):
    """
    通用字段(创建人、创建时间、更新人、更新时间) model Manager
    """

    def get_queryset(self):
        """获取queryset"""
        return OperateRecordQuerySet(self.model, using=self._db)

    def create(self, *args, **kwargs):
        """创建数据 自动填写通用字段"""
        kwargs.update(
            {
                "created_at": kwargs.get("created_at") or timezone.now(),
                "created_by": kwargs.get("created_by") or get_request_username(),
                "updated_at": kwargs.get("updated_at") or timezone.now(),
                "updated_by": kwargs.get("updated_by") or get_request_username(),
            }
        )
        return super().create(*args, **kwargs)

    def bulk_create(self, objs, *args, **kwargs):
        """创建数据 自动填写通用字段"""
        for obj in objs:
            obj.created_at = obj.created_at or timezone.now()
            obj.created_by = obj.created_by or get_request_username()
            obj.updated_at = timezone.now()
            obj.updated_by = get_request_username()
        return super().bulk_create(objs, *args, **kwargs)

    def bulk_update(self, objs, *args, **kwargs):
        """更新数据 自动填写通用字段"""
        for obj in objs:
            obj.created_at = obj.created_at or timezone.now()
            obj.created_by = obj.created_by or get_request_username()
            obj.updated_at = timezone.now()
            obj.updated_by = get_request_username()
        return super().bulk_update(objs, *args, **kwargs)


class OperateRecordModel(models.Model):
    """
    需要记录操作的model父类
    自动记录创建时间/修改时间与操作者
    """

    objects = OperateRecordModelManager()

    origin_objects = models.Manager()

    created_at = models.DateTimeField(_("创建时间"), db_index=True, default=timezone.now)

    created_by = models.CharField(_("创建者"), max_length=32, default="", db_index=True, null=True)
    updated_at = models.DateTimeField(
        _("更新时间"),
        blank=True,
        null=True,
    )
    updated_by = models.CharField(_("修改者"), max_length=32, blank=True, default="", null=True)

    def save(self, *args, **kwargs):
        """
        Save the current instance. Override this in a subclass if you want to
        control the saving process.

        The 'force_insert' and 'force_update' parameters can be used to insist
        that the "save" must be an SQL insert or update (or equivalent for
        non-SQL backends), respectively. Normally, they should not be set.
        """
        operator = get_request_username()

        if not self.pk:
            self.created_by = operator
            self.created_at = timezone.now()

        if not self.created_by:
            self.created_by = operator

        self.updated_at = timezone.now()

        self.updated_by = operator
        if kwargs.get("update_fields"):
            kwargs["update_fields"] = [*set(kwargs["update_fields"]), "updated_by", "updated_at"]
        super().save(*args, **kwargs)

    class Meta:
        """元数据定义"""

        abstract = True


class SoftDeleteQuerySet(OperateRecordQuerySet):
    """
    软删除Queryset
    """

    def filter(self, *args, **kwargs):
        if "is_deleted" in kwargs:
            # 当前已经含is_deleted条件则跳过
            return super().filter(*args, **kwargs)
        for child in self.query.where.children:
            if isinstance(child, Exact) and child.lhs.field.name == "is_deleted":
                self.query.where.children.pop()
        return super().filter(*args, **kwargs).filter(is_deleted=False)

    def all(self, *args, **kwargs):
        return super().all(*args, **kwargs).filter(is_deleted=False)

    def delete(self):
        self.update(
            is_deleted=True,
            updated_by=get_request_username(),
            updated_at=timezone.now(),
        )


class SoftDeleteModelManager(OperateRecordModelManager):
    """
    默认的查询和过滤方法, 不显示被标记为删除的记录
    """

    def get_queryset(self):
        """获取queryset"""
        return SoftDeleteQuerySet(self.model, using=self._db)

    def all(self):
        return self.get_queryset().filter()


class HardDeletedManager(models.Manager):
    pass


class SoftDeleteModel(OperateRecordModel):
    """
    需要记录删除操作的model父类
    自动记录删除时间与删除者
    对于此类的表提供软删除
    """

    objects = SoftDeleteModelManager()
    hard_deleted_objects = HardDeletedManager()

    is_deleted = models.BooleanField(_("是否删除"), default=False)

    def delete(self, *args, **kwargs):  # pylint: disable=unused-argument
        """
        删除方法，不会删除数据
        而是通过标记删除字段 is_deleted 来软删除
        """
        self.is_deleted = True
        self.save()

    class Meta:
        """元数据定义"""

        abstract = True


class MultiStrSplitFieldMixin(models.Field):
    """
    多个字段，使用逗号隔开，入库list->str， 出库 str->list
    头尾都加逗号","，为了方便使用ORM的contains进行过滤且避免子集字符串的越权问题
    """

    def read_from_db(self, value, expression, connection):  # pylint: disable=unused-argument
        """
        从db读取 -> 转为列表
        """
        if not value:
            return []
        try:
            value = value.split(",")
        except (TypeError, KeyError):
            raise exceptions.ValidationError(
                self.error_messages["invalid"],
                code="invalid",
                params={"value": value},
            )
        result = []
        # 去除头尾逗号
        for _v in value[1:-1]:
            try:
                result.append(self.sub_type(_v))
            except ValueError:
                continue

        return result

    def write_to_db(self, value: [int, str, List]):
        """
        写入db -> 通过,拼街
        """
        if not value:
            return ""

        if isinstance(value, str):
            value_list = [item.strip() for item in value.strip().strip(",").split(",") if item and item.strip()]
        else:
            value_list = [str(_value).strip() for _value in value if _value and str(_value).strip()]
        try:
            value = f",{','.join(value_list)},"
            return value
        except (TypeError, KeyError):
            raise exceptions.ValidationError(
                self.error_messages["invalid"],
                code="invalid",
                params={"value": value},
            )


class MultiStrSplitCharField(models.CharField, MultiStrSplitFieldMixin):
    """
    ORM Char字符串列表字段
    """

    def __init__(self, *args, **kwargs):
        self.sub_type = kwargs.get("sub_type") or str
        kwargs.pop("sub_type", "")
        super().__init__(*args, **kwargs)

    def from_db_value(self, value, expression, connection):
        """
        从DB读取 与MultiStrSplitFieldMixin一致
        """
        return super().read_from_db(value, expression, connection)

    def get_prep_value(self, value):
        """Perform preliminary non-db specific value checks and conversions."""
        return super().write_to_db(value)


class MultiStrSplitTextField(models.TextField, MultiStrSplitFieldMixin):
    """
    ORM Text字符串列表字段
    """

    def __init__(self, *args, **kwargs):
        self.sub_type = kwargs.get("sub_type") or str
        kwargs.pop("sub_type", "")
        super().__init__(*args, **kwargs)

    def from_db_value(self, value, expression, connection):
        """
        从DB读取 与MultiStrSplitFieldMixin一致
        """
        return super().read_from_db(value, expression, connection)

    def get_prep_value(self, value):
        """Perform preliminary non-db specific value checks and conversions."""
        return super().write_to_db(value)


class ModelResourceMixin:
    view_set_attrs = {
        "pagination_class": api_settings.DEFAULT_PAGINATION_CLASS,
        "ordering_fields": ["created_at"],
    }
    serializer_free_actions = ["list", "retrieve"]
    ignore_request_serializer = True
    request_data = None

    def validate_request_data(self, request_data: Dict):
        """
        去掉 RequestSerializer校验，仅用于生成swagger
        """
        if self.serializer_class:
            try:
                if (
                    self.ignore_request_serializer
                    and hasattr(self, "action")
                    and self.action not in self.serializer_free_actions
                ):
                    self._request_serializer = None
                    return request_data
            except NotImplementedError:
                pass

        return super().validate_request_data(request_data)


class OptionType(TextChoices):
    # 选项类型
    TYPE_BOOL = "bool", "bool"
    TYPE_STRING = "string", "string"
    TYPE_LIST = "list", "list"
    TYPE_DICT = "dict", "dict"
    TYPE_INT = "int", "int"
    TYPE_DATETIME = "datetime", "datetime"
    TYPE_NONE = "null", "null"


class OptionBase(SoftDeleteModel):
    """各种选项配置的基类，供结果表选项，结果表字段选项，数据源选项继承"""

    QUERY_NAME = None

    # 选项类型
    TYPE_BOOL = "bool"
    TYPE_STRING = "string"
    TYPE_LIST = "list"
    TYPE_DICT = "dict"
    TYPE_INT = "int"
    TYPE_DATETIME = "datetime"
    TYPE_NONE = "null"

    TYPE_OPTION_DICT = {TYPE_STRING: str, TYPE_DATETIME: str}

    value_type = models.CharField(_("option对应类型"), choices=OptionType.choices, max_length=LEN_NORMAL)
    value = models.TextField(_("option配置内容"))

    class Meta:
        abstract = True

    @classmethod
    def get_option(cls, query_id: str) -> Dict:
        """
        返回一个指定的option配置内容
        :param query_id: 查询的ID名
        :return: {
            "option_name": option_value
        }
        """
        query_dict = {cls.QUERY_NAME: query_id}
        option_dict = {}

        for instance in cls.objects.filter(**query_dict):
            option_dict.update(instance.to_json())

        return option_dict

    @classmethod
    def _parse_value(cls, value: Any) -> Tuple[Any, str]:
        """计算值的类型 ."""
        if value is None:
            val, val_type = ("", cls.TYPE_NONE)
        elif isinstance(value, (bool, list, dict)):
            val = json.dumps(value)

            if isinstance(value, bool):
                val_type = cls.TYPE_BOOL
            elif isinstance(value, list):
                val_type = cls.TYPE_LIST
            else:
                val_type = cls.TYPE_DICT
        elif isinstance(value, int):
            val = json.dumps(value)
            val_type = cls.TYPE_INT
        elif isinstance(value, datetime):
            val = value.strftime("%Y-%m-%d %X")
            val_type = cls.TYPE_DATETIME
        else:
            val, val_type = value, cls.TYPE_STRING

        return val, val_type

    @classmethod
    def create_option(cls, value):
        """
        创建字段对象，不保存
        :param value: 选项值
        :return: object
        """
        new_object = cls()

        new_object.value, new_object.value_type = cls._parse_value(value)

        return new_object

    def _trans_list(self):
        """
        将保存的内容按照list的类型进行返回
        :return: list object
        """

        return json.loads(self.value)

    def _trans_bool(self):
        """
        将保存的内容按照list的类型进行返回
        :return: list object
        """

        return json.loads(self.value)

    def _trans_dict(self):
        """
        将保存的内容按照dict的类型进行返回
        :return: dict object
        """

        return json.loads(self.value)

    def _trans_int(self):
        return json.loads(self.value)

    def _trans_null(self):
        return ""

    def to_json(self):
        """
        将一个配置变为字典内容返回
        :return: {
            "option_name": option_value
        }
        """
        try:
            # 先匹配特殊逻辑
            value_type = self.TYPE_OPTION_DICT[self.value_type]
            real_value = value_type(self.value) if self.value_type != "string" else str(self.value)
        except KeyError:
            # 如果找不到对应的配置，表示不是简单的基本功能，需要依赖函数实现
            trans_method = getattr(self, "_trans_{}".format(self.value_type))
            real_value = trans_method()

        return {self.name: real_value}


class ChangeHistoryBase(OptionBase):
    new_value = models.TextField(_("新数据"))
    new_value_type = models.CharField(
        _("新值的类型"),
        max_length=64,
    )

    def to_json(self):
        """
        将一个配置变为字典内容返回
        :return: {
            "option_name": option_value
        }
        """
        try:
            value_type = self.TYPE_OPTION_DICT[self.value_type]
            old_value = value_type(self.value) if self.value_type != "string" else str(self.value)
        except KeyError:
            if self.value is None or self.value == "":
                old_value = None
            else:
                old_value = json.loads(self.value)
        try:
            new_value_type = self.TYPE_OPTION_DICT[self.new_value_type]
            new_value = new_value_type(self.new_value) if self.new_value_type != "string" else str(self.new_value)
        except KeyError:
            if self.new_value is None or self.new_value == "":
                new_value = None
            else:
                new_value = json.loads(self.new_value)

        return {
            "name": self.name,
            "value": old_value,
            "new_value": new_value,
            "value_type": self.value_type,
            "new_value_type": self.new_value_type,
        }

    @classmethod
    def create_option(cls, value, new_value):
        """
        创建字段对象，不保存
        :param value: 选项值
        :param new_value: 新的值
        :return: object
        """
        new_object = cls()

        new_object.value, new_object.value_type = cls._parse_value(value)
        new_object.new_value, new_object.new_value_type = cls._parse_value(new_value)

        return new_object

    class Meta:
        abstract = True


class UUIDField(models.CharField):
    def __init__(self, *args, **kwargs):
        kwargs.update({"default": UUIDField.get_default_value, "max_length": max(64, kwargs.get("max_length", 0))})
        super().__init__(*args, **kwargs)

    @classmethod
    def get_default_value(cls) -> str:
        return uuid.uuid1().hex


def get_verbose_name(queryset=None, view=None, model=None) -> str:
    """
    获取模型的 verbose_name
    """
    try:
        if queryset is not None and hasattr(queryset, "model"):
            model = queryset.model
        elif view and hasattr(view.get_queryset(), "model"):
            model = view.get_queryset().model
        elif view and hasattr(view.get_serializer(), "Meta") and hasattr(view.get_serializer().Meta, "model"):
            model = view.get_serializer().Meta.model
        if model:
            return getattr(model, "_meta").verbose_name
        else:
            model = queryset.model._meta.verbose_name
    except Exception:
        pass

    return model if model else ""


def get_model_from_app(app_name: str) -> List:
    """获取模型里的字段"""
    model_module = import_module(app_name + ".models")
    filter_model = [
        getattr(model_module, item)
        for item in dir(model_module)
        if issubclass(getattr(model_module, item).__class__, models.base.ModelBase)
    ]
    model_list = []
    for model in filter_model:
        model_name = model.__name__
        verbose_name = model._meta.verbose_name
        if model_name in ["AbstractUser", "OptionBase"]:
            continue
        if getattr(model._meta, "abstract", False):
            continue
        fields = [{"title": field.verbose_name, "name": field.name, "object": field} for field in model._meta.fields]
        model_list.append(
            {
                "app": app_name,
                "verbose": verbose_name,
                "model": model_name,
                "object": model,
                "fields": fields,
            }
        )

    return model_list


def get_custom_app_models(app_name=None):
    """
    获取所有项目下的app里的models
    """
    if app_name:
        return get_model_from_app(app_name)
    all_apps = apps.get_app_configs()
    res = []
    for app in all_apps:
        if app.name.startswith("django"):
            continue
        if app.name in settings.COLUMN_EXCLUDE_APPS:
            continue
        try:
            all_models = get_model_from_app(app.name)
            if all_models:
                for model in all_models:
                    res.append(model)
        except Exception:
            pass
    return res
