import pytest

from apps.snippets.models import Snippet


class TestSnippet:

    @pytest.mark.django_db
    def test_save(self):
        snippet = Snippet(code='foo = "bar"\n')
        snippet.save()

        snippet = Snippet(code='print("hello, world")\n')
        snippet.save()
