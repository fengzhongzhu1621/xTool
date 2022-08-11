# -*- coding: utf-8 -*-

from django.utils.translation import ugettext_lazy as _lazy
from xTool.django.core.errors import HttpError


class HttpErrorExample(HttpError):
    code = 999
    message = _lazy("message error")
    message_template = _lazy("message erro come from {name}")


class TestHttpError():

    def test_message(self):
        error_1 = HttpErrorExample()
        assert str(error_1) == "message error"

        error_2 = HttpErrorExample(name="template")
        assert str(error_2) == "message erro come from template"
