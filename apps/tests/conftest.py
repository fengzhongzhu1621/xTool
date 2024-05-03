# -*- coding: utf-8 -*-
import arrow
import pytest
from django.conf import settings
from django.utils.functional import empty

from apps.credential.models import CredentialResource, Credential


def pytest_configure():
    # 添加需要修改的配置到 config_dict 中
    config_dict = {}
    if settings._wrapped is empty:
        settings.configure(**config_dict)


@pytest.fixture
def credential():
    CredentialResource.hard_deleted_objects.all().delete()
    Credential.hard_deleted_objects.all().delete()

    params = {
        "token": "xxx",
        "name": "name",
        "begin_time": arrow.get("2024-01-02 03:04:05").datetime,
        "end_time": arrow.get("2024-02-02 03:04:05").datetime,
        "desc": "desc",
    }
    instance = Credential.objects.create(**params)

    params = {
        "credential": instance,
        "resource_type": "type_1",
        "filter_condition": [
            {
                'field': 'operator',
                'op': 'eq',
                'value': "admin",
            },
            {
                'field': 'username',
                'op': 'eq',
                'value': "username_1",
            },
        ],
    }
    CredentialResource.objects.create(**params)

    return instance
