import pytest

from apps.http_client.resources import SendRequestResource

pytestmark = pytest.mark.django_db


class TestSendRequestResource:

    def test_perform_request(self, request_system_config, request_api_config, monkeypatch_request_api_config):
        request_context = {
            "a": "value_a",
            "b": "value_b",
        }
        params = {
            "system_code": request_system_config.code,
            "api_code": request_api_config.code,
            "request_context": request_context,
        }
        actual = SendRequestResource()(params)
        expect = {"code": 0}
        assert actual == expect
