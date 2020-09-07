# -*- coding: utf-8 -*-

import pytest
from xTool.decorators.reify import reify_py, reify_c


class ReifyMixin:

    reify = NotImplemented

    def test_reify(self) -> None:
        class A:
            def __init__(self):
                self._cache = {}

            @self.reify
            def prop(self):
                return 1

        a = A()
        assert 1 == a.prop

    def test_reify_class(self) -> None:
        class A:
            def __init__(self):
                self._cache = {}

            @self.reify
            def prop(self):
                """Docstring."""
                return 1

        assert isinstance(A.prop, self.reify)
        assert 'Docstring.' == A.prop.__doc__

    def test_reify_assignment(self) -> None:
        class A:
            def __init__(self):
                self._cache = {}

            @self.reify
            def prop(self):
                return 1

        a = A()

        with pytest.raises(AttributeError):
            a.prop = 123


class TestPyReify(ReifyMixin):
    reify = reify_py
