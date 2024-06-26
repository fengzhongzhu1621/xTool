from django.utils.translation import gettext_lazy as _lazy

from core.errors import HttpError


class HttpErrorExample(HttpError):
    code = 999
    message = _lazy("message error")
    message_template = _lazy("message error come from {name}")


class TestHttpError:

    def test_message(self):
        error_1 = HttpErrorExample()
        assert str(error_1) == "message error"

        error_2 = HttpErrorExample(name="template")
        assert str(error_2) == "message error come from template"
