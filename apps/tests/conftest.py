import arrow
import pytest
from django.conf import settings
from django.utils.functional import empty

from apps.credential.models import Credential, CredentialResource
from apps.http_client.models import RequestApiConfig, RequestSystemConfig
from apps.http_client.resources import RequestApiConfigResource


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
                "field": "operator",
                "op": "eq",
                "value": "admin",
            },
            {
                "field": "username",
                "op": "eq",
                "value": "username_1",
            },
        ],
    }
    CredentialResource.objects.create(**params)

    return instance


@pytest.fixture
def request_system_config() -> RequestSystemConfig:
    RequestSystemConfig.hard_deleted_objects.all().delete()

    instance = RequestSystemConfig.objects.create(
        **{
            "name": "system_name",
            "code": "system_code",
            "desc": "desc",
            "owners": "owners_1",
            "domain": "https://xxxxxxxxxx.com",
        }
    )

    return instance


@pytest.fixture
def request_api_config(request_system_config) -> RequestApiConfig:
    RequestApiConfig.hard_deleted_objects.all().delete()
    instance = RequestApiConfig.objects.create(
        **{
            "system": request_system_config,
            "code": "api_code",
            "name": "api_name",
            "path": "/path",
            "method": "GET",
            "request_params": {
                "a": "{{a}}",
                "b": "{{b}}",
            },
        }
    )

    return instance


@pytest.fixture
def monkeypatch_request_api_config(monkeypatch):
    monkeypatch.setattr(
        RequestApiConfigResource,
        "perform_request",
        lambda _self, params: {
            "code": 0,
        },
    )
