import cryptography  # noqa
import jwt
from django.conf import settings
from jwt import exceptions as jwt_exceptions

from apps.logger import logger
from xTool.algorithms.collections import FancyDict


class JWTClient:
    def __init__(self, request):
        self.request = request
        # 从请求头获取JWT加密内容
        header_name = getattr(settings, "APIGW_JWT_KEY", "HTTP_X_BKAPI_JWT")
        self.raw_content = request.META.get(header_name, "")
        self.error_message = ""
        self.is_valid = False

        self.payload = {}
        self.headers = {}
        self.get_jwt_info()

        self.app = self.get_app_model()
        self.user = self.get_user_model()

    def get_app_model(self):
        return FancyDict(self.payload.get("app", {}))

    def get_user_model(self):
        return FancyDict(self.payload.get("user", {}))

    def get_jwt_info(self):
        if not self.raw_content:
            self.error_message = "X_BKAPI_JWT not in http header or it is empty, please called API through API Gateway"
            return False
        # 使用公钥解密 jwt 内容
        try:
            self.headers = jwt.get_unverified_header(self.raw_content)
            self.payload = jwt.decode(self.raw_content, settings.APIGW_PUBLIC_KEY, issuer="APIGW")
            self.is_valid = True
        except jwt_exceptions.InvalidKeyError:
            self.error_message = "APIGW_PUBLIC_KEY error"
        except jwt_exceptions.DecodeError:
            self.error_message = "Invalid X_BKAPI_JWT, wrong format or value"
        except jwt_exceptions.ExpiredSignatureError:
            self.error_message = "Invalid X_BKAPI_JWT, which is expired"
        except jwt_exceptions.InvalidIssuerError:
            self.error_message = "Invalid X_BKAPI_JWT, which is not from API Gateway"
        except Exception as error:
            self.error_message = error.message

        if self.error_message:
            logger.exception("[jwt_client] decode jwt fail, err: %s" % self.error_message)

    def __str__(self):
        return "<{headers}, {payload}>".format(headers=self.headers, payload=self.payload)
