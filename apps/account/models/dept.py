from typing import List

from django.db import models
from django.utils.translation import gettext_lazy as _lazy

from core.constants import LEN_NORMAL, LEN_SHORT
from core.models import SoftDeleteModel


class DeptManager:
    def recursion_all_dept(self, dept_id: int, dept_all_list=None, dept_list=None) -> List:
        """
        递归获取部门的所有下级部门
        :param dept_id: 需要获取的id
        :param dept_all_list: 所有列表
        :param dept_list: 递归list
        :return:
        """
        if not dept_all_list:
            dept_all_list = self.values("id", "parent")
        if dept_list is None:
            dept_list = [dept_id]
        for ele in dept_all_list:
            if ele.get("parent") == dept_id:
                dept_list.append(ele.get("id"))
                self.recursion_all_dept(ele.get("id"), dept_all_list, dept_list)
        return list(set(dept_list))


class Dept(SoftDeleteModel):
    name = models.CharField(max_length=LEN_NORMAL, verbose_name=_lazy("部门名称"))
    key = models.CharField(max_length=LEN_NORMAL, unique=True, null=True, blank=True, verbose_name=_lazy("关联字符"))
    sort = models.IntegerField(default=1, verbose_name=_lazy("显示排序"))
    owner = models.CharField(max_length=LEN_NORMAL, verbose_name=_lazy("负责人"), null=True, blank=True)
    phone = models.CharField(max_length=LEN_SHORT, verbose_name=_lazy("联系电话"), null=True, blank=True)
    email = models.EmailField(max_length=LEN_SHORT, verbose_name=_lazy("邮箱"), null=True, blank=True)
    status = models.BooleanField(default=True, verbose_name=_lazy("部门状态"), null=True, blank=True)
    parent = models.ForeignKey(
        to="Dept",
        on_delete=models.CASCADE,
        default=None,
        verbose_name=_lazy("上级部门"),
        db_constraint=False,
        null=True,
        blank=True,
    )

    objects = DeptManager

    class Meta:
        app_label = "account"
        verbose_name = _lazy("部门表")
        verbose_name_plural = verbose_name
