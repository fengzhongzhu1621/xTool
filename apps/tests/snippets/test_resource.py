# -*- coding: utf-8 -*-

import pytest

from apps.core.drf_resource import ModelResource
from apps.snippets.models import Snippet
from apps.snippets.serializers import SnippetSerializer

pytestmark = pytest.mark.django_db


class SnippetViewSet(ModelResource):
    """
    This viewset automatically provides `list`, `create`, `retrieve`,
    `update` and `destroy` actions.

    Additionally we also provide an extra `highlight` action.
    """
    queryset = Snippet.objects.all()
    serializer_class = SnippetSerializer

    action = "list"
    method = "get"


class TestSnippetViewSet:

    def test_perform_request(self):
        actual = SnippetViewSet().request({
            "a": 1
        })
        assert actual == []
