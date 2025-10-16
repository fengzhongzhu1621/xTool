from django.db import models
from django.utils.translation import gettext_lazy as _lazy

from core.constants import LEN_LONG, LEN_MIDDLE, LEN_NORMAL, LEN_SHORT, RequestMethod
from core.models import SoftDeleteModel, SoftDeleteModelManager


class MenuManager(SoftDeleteModelManager):
    def get_all_parent(self, menu_id: int, all_list=None, nodes=None):
        """
        递归获取给定ID的所有层级
        :param menu_id: 参数ID
        :param all_list: 所有列表
        :param nodes: 递归列表
        :return: nodes
        """
        if not all_list:
            all_list = Menu.objects.values("id", "name", "parent")
        if nodes is None:
            nodes = []
        for ele in all_list:
            if ele.get("id") == menu_id:
                parent_id = ele.get("parent")
                if parent_id is not None:
                    self.get_all_parent(parent_id, all_list, nodes)
                nodes.append(ele)
        return nodes


class Menu(SoftDeleteModel):
    parent = models.ForeignKey(
        to="Menu", on_delete=models.CASCADE, verbose_name=_lazy("上级菜单"), null=True, blank=True, db_constraint=False
    )
    icon = models.CharField(max_length=LEN_NORMAL, verbose_name=_lazy("菜单图标"), null=True, blank=True)
    name = models.CharField(max_length=LEN_NORMAL, verbose_name=_lazy("菜单名称"))
    sort = models.IntegerField(default=1, verbose_name=_lazy("显示排序"), null=True, blank=True)
    is_link = models.BooleanField(default=False, verbose_name=_lazy("是否外链"))
    link_url = models.CharField(max_length=LEN_LONG, verbose_name=_lazy("链接地址"), null=True, blank=True)
    is_catalog = models.BooleanField(default=False, verbose_name=_lazy("是否目录"))
    web_path = models.CharField(max_length=LEN_MIDDLE, verbose_name=_lazy("路由地址"), null=True, blank=True)
    component = models.CharField(max_length=LEN_MIDDLE, verbose_name=_lazy("组件地址"), null=True, blank=True)
    component_name = models.CharField(max_length=LEN_NORMAL, verbose_name=_lazy("组件名称"), null=True, blank=True)
    status = models.BooleanField(default=True, blank=True, verbose_name=_lazy("菜单状态"))
    cache = models.BooleanField(default=False, blank=True, verbose_name=_lazy("是否页面缓存"))
    visible = models.BooleanField(default=True, blank=True, verbose_name=_lazy("侧边栏中是否显示"))
    is_iframe = models.BooleanField(default=False, blank=True, verbose_name=_lazy("框架外显示"))
    is_affix = models.BooleanField(default=False, blank=True, verbose_name=_lazy("是否固定"))

    class Meta:
        app_label = "account"
        verbose_name = _lazy("菜单表")
        verbose_name_plural = verbose_name


class MenuField(SoftDeleteModel):
    model = models.CharField(max_length=LEN_NORMAL, verbose_name=_lazy("表名"))
    menu = models.ForeignKey(to="Menu", on_delete=models.CASCADE, verbose_name=_lazy("菜单"), db_constraint=False)
    field_name = models.CharField(max_length=LEN_NORMAL, verbose_name=_lazy("模型表字段名"))
    title = models.CharField(max_length=LEN_NORMAL, verbose_name=_lazy("字段显示名"))

    class Meta:
        app_label = "account"
        verbose_name = _lazy("菜单字段表")
        verbose_name_plural = verbose_name


class MenuButton(SoftDeleteModel):
    menu = models.ForeignKey(
        to="Menu",
        db_constraint=False,
        related_name="menuPermission",
        on_delete=models.CASCADE,
        verbose_name=_lazy("关联菜单"),
    )
    name = models.CharField(max_length=LEN_NORMAL, verbose_name=_lazy("名称"))
    value = models.CharField(unique=True, max_length=LEN_NORMAL, verbose_name=_lazy("权限值"))
    api = models.CharField(max_length=LEN_LONG, verbose_name=_lazy("接口地址"))
    method = models.CharField(
        max_length=LEN_SHORT, verbose_name=_lazy("接口请求方法"), choices=RequestMethod.choices, null=True, blank=True
    )

    class Meta:
        verbose_name = _lazy("菜单按钮表")
        verbose_name_plural = verbose_name
