# -*- coding: utf-8 -*-
import pytest

from apps.snippets.models import Snippet


@pytest.fixture
def add_snippet_models():
    snippet = Snippet(code='print("hello, world")\n')
    snippet.save()
