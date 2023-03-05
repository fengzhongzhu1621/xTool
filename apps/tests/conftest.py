# -*- coding: utf-8 -*-
from django.conf import settings
from django.utils.functional import empty


def pytest_configure():
    # 添加需要修改的配置到 config_dict 中
    config_dict = {}
    if settings._wrapped is empty:
        settings.configure(**config_dict)
