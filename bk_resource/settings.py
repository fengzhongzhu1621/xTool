from collections import defaultdict
from typing import Union

from django.conf import settings
from django.utils.module_loading import import_string


class BkResourceSettings():
    """
    Settings
    """

    SETTINGS = defaultdict(
        None,
        DEFAULT_API_DIR="api",
        DEFAULT_RESOURCE_DIRS=[],
        LOCAL_CACHE_ENABLE=False,
        INTERFACE_COMMON_PARAMS={
            "bk_app_code": settings.APP_CODE,
            "bk_app_secret": settings.SECRET_KEY,
        },
        DEFAULT_ERROR_RESPONSE_SERIALIZER="bk_resource.serializers.ErrorResponseSerializer",
        DEFAULT_PAGINATOR_RESPONSE_BUILDER="bk_resource.serializers.PaginatorResponseBuilder",
        DEFAULT_STANDARD_RESPONSE_BUILDER="bk_resource.serializers.StandardResponseBuilder",
        DEFAULT_SWAGGER_SCHEMA_CLASS="bk_resource.utils.inspectors.BkResourceSwaggerAutoSchema",
        REQUEST_LOG_HANDLER="bk_resource.utils.request_log.RequestLogHandler",
        REQUEST_LOG_SPLIT_LENGTH=0,
        REQUEST_VERIFY=True,
        PLATFORM_AUTH_ENABLED=False,
        PLATFORM_AUTH_ACCESS_TOKEN=None,
        PLATFORM_AUTH_ACCESS_USERNAME=None,
        REQUEST_BKAPI_COOKIE_FIELDS=["blueking_language", "django_language"],
        REQUEST_LANGUGAE_HEADER_KEY="blueking-language",
        RESOURCE_BULK_REQUEST_PROCESSES=None,
    )

    LAZY_IMPORT_SETTINGS = (
        "DEFAULT_ERROR_RESPONSE_SERIALIZER",
        "DEFAULT_PAGINATOR_RESPONSE_BUILDER",
        "DEFAULT_STANDARD_RESPONSE_BUILDER",
        "DEFAULT_SWAGGER_SCHEMA_CLASS",
        "REQUEST_LOG_HANDLER",
    )

    LOADED_SETTINGS = {}

    def __getattr__(self, key: str) -> any:
        """
        get settings from self
        """

        # 0. validate key
        self.__validate_key(key)

        # 1. load Key from cache
        if key in self.LOADED_SETTINGS.keys():
            return self.LOADED_SETTINGS[key]

        # 2. load key from django.conf.settings
        if key in self.custom_settings.keys():
            return self.__load_key(key, self.custom_settings[key])

        # 3. load key from default settings
        return self.__load_key(key, self.SETTINGS[key])

    def __validate_key(self, key: str) -> None:
        """
        validate key
        """

        if key not in self.SETTINGS.keys():
            raise KeyError("[%s] is not a valid key for bk_resource" % key)

    def __load_key(self, key: str, val: Union[str, callable]) -> any:
        """
        load lazy import key to cache
        """

        # load lazy setting
        if key in self.LAZY_IMPORT_SETTINGS and isinstance(val, str):
            val = import_string(val)
            self.LOADED_SETTINGS[key] = val

        # return value
        return val

    @property
    def custom_settings(self) -> dict:
        """
        Custom settings in django.conf.settings
        """

        return getattr(settings, "BK_RESOURCE", {})


bk_resource_settings = BkResourceSettings()
