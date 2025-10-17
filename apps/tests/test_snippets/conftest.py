import pytest

from apps.snippets.models import Snippet

pytestmark = pytest.mark.django_db


@pytest.fixture
def add_snippet_models():
    snippet = Snippet(code='print("hello, world")\n')
    snippet.save()
