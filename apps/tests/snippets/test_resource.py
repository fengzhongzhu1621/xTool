# -*- coding: utf-8 -*-

import pytest

from apps.core.drf_resource import ModelResource
from apps.snippets.models import Snippet
from apps.snippets.serializers import SnippetSerializer
from rest_framework import renderers
from rest_framework.decorators import action
from rest_framework.response import Response

pytestmark = pytest.mark.django_db


class SnippetViewSetResource(ModelResource):
    queryset = Snippet.objects.all()
    serializer_class = SnippetSerializer

    @action(detail=True, renderer_classes=[renderers.StaticHTMLRenderer])
    def highlight(self, request, *args, **kwargs):
        snippet = self.get_object()
        return Response(snippet.highlighted)

    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        return response


class TestSnippetViewSet:

    def test_perform_request(self):
        actual = SnippetViewSetResource().request({
            "a": 1
        }, action="list")
        assert actual == []

        # actual = SnippetViewSetResource().request({
        #     "id": 1,
        #     "a": 1
        # }, action="highlight")
        # assert actual == []
