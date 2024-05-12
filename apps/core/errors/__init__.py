from django.utils.translation import gettext_lazy as _lazy


class HttpError(Exception):
    status_code = 500
    code = -1
    message = _lazy("系统异常，请联系管理员")
    message_template = _lazy("系统异常，请联系管理员")

    def __init__(self, data=None, extra=None, **kwargs) -> None:
        self.data = data
        self.extra = extra if extra else {}
        if kwargs:
            try:
                self.message = self.message_template.format(**kwargs)
            except Exception:  # noqa
                pass

    def __str__(self) -> str:
        return str(self.message)
