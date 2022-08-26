# -*- coding: utf-8 -*-

import pytest

from apps.snippets.models import Snippet
from apps.snippets.serializers import SnippetSerializer

pytestmark = pytest.mark.django_db


class TestSnippetSerializer:

    def test_data(self):
        snippet = Snippet(code='print("hello, world")\n')
        snippet.save()

        serializer = SnippetSerializer(snippet)
        serializer.data
