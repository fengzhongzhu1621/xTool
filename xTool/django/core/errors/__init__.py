# -*- coding: utf-8 -*-

from django.utils.translation import ugettext_lazy as _lazy


class HttpError(Exception):
    status_code = 500
    code = 0
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

    def __str__(self):
        return str(self.message)
