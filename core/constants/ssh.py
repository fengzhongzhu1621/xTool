from django.db.models import TextChoices
from django.utils.translation import gettext_lazy as _lazy


class SSLEnum(TextChoices):
    SERVER_CRT = "server.crt", _lazy("服务器证书文件")
    SERVER_KEY = "server.key", _lazy("服务器私钥")
    CLIENT_CRT = "client.crt", _lazy("客户端证书文件")
    CLIENT_KEY = "client.key", _lazy("客户端私钥")
