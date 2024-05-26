from typing import Dict, List, Optional

import pytest
from rest_framework import serializers
from rest_framework.exceptions import APIException

from core.drf_resource import api
from core.drf_resource.base import Resource


# @register_plugin(PluginType.drf_resource, "MockResource")
class MockResource(Resource):
    plugin_type = "test"

    def perform_request(self, validated_request_data: Optional[Dict] = None) -> List:
        if validated_request_data:
            return validated_request_data
        return ["hello world"]


class MockResourceWithRequestSerializer(MockResource):
    class RequestSerializer(serializers.Serializer):
        name = serializers.CharField(label="name", required=True)


class TestResource:

    def test_perform_request__no_params(self):
        actual = MockResource().request()
        assert actual == ["hello world"]
        actual = MockResource()()
        assert actual == ["hello world"]

    def test_perform_request__params_existed(self):
        actual = MockResource().request({"a": 1})
        assert actual == {"a": 1}
        actual = MockResource()({"a": 1})
        assert actual == {"a": 1}

    def test_validate_request_data(self):
        with pytest.raises(APIException):
            MockResourceWithRequestSerializer().request({"a": 1})
        with pytest.raises(APIException):
            MockResourceWithRequestSerializer().request()
        actual = MockResourceWithRequestSerializer().request({"name": "a"})
        assert actual == {"name": "a"}


def test_api():
    actual = api.test.MockResource.request()
    assert actual == ["hello world"]
    actual = api.test.MockResource()
    assert actual == ["hello world"]
