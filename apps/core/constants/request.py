from django.db.models import TextChoices
from django.utils.translation import gettext_lazy as _lazy


class RequestMethod(TextChoices):
    """HTTP请求方法 ."""

    GET = "GET", _lazy("GET")
    POST = "POST", _lazy("POST")
    PUT = "PUT", _lazy("PUT")
    PATCH = "PATCH", _lazy("PATCH")
    DELETE = "DELETE", _lazy("DELETE")
