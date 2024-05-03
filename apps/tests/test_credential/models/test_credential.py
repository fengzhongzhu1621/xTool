import pytest

from apps.credential.models import Credential

pytestmark = pytest.mark.django_db


class TestCredential:
    def test_read_conf(self, credential):
        token = credential.token
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
                }
            ],
            "token": "xxx",
        }

        assert actual == expect
