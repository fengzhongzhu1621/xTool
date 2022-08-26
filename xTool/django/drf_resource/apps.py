# -*- coding: utf-8 -*-

from django.apps import AppConfig


class DrfResourceAppConfig(AppConfig):
    # 指向此应用程序的完整的 Python 格式的路径
    # 每个 AppConfig 子类都必须包含此项。
    # 它必须在整个 Django 项目中唯一。
    name = "xTool.django.drf_resource"
    # 应用程序容易被人理解的名称，如 “Administration”。
    # 此属性默认值为 label.title()。
    verbose_name = "drf_resource"
    # 应用程序简称
    # 允许在两个应用标签冲突时重命名其中一个的标签名。默认是 name 的最后一段。必须是一个有效的 Python 标识符
    # 必须在整个 Django 项目中唯一
    label = "drf_resource"
