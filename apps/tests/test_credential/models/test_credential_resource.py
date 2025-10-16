import pytest

from apps.credential.models import Credential, CredentialResource

pytestmark = pytest.mark.django_db


class TestCredentialResource:
    def test_refresh_cache(self, credential):
        token = credential.token

        params = {
            "credential": credential,
            "resource_type": "type_2",
            "filter_condition": [
                {
                    "field": "group",
                    "op": "in",
                    "value": [
                        "group_1",
                    ],
                },
            ],
        }
        CredentialResource.objects.create(**params)

        actual = Credential.objects.read_conf(token)
        expect = {
            "begin_time": "2024-01-02 03:04:05+00:00",
            "end_time": "2024-02-02 03:04:05+00:00",
            "resources": [
                {
                    "filter_condition": [
                        {"field": "operator", "op": "eq", "value": "admin"},
                        {"field": "username", "op": "eq", "value": "username_1"},
                    ],
                    "resource_type": "type_1",
                },
                {
                    "filter_condition": [{"field": "group", "op": "in", "value": ["group_1"]}],
                    "resource_type": "type_2",
                },
            ],
            "token": "xxx",
        }

        assert actual == expect
