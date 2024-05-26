from collections import defaultdict

from django.conf import settings

from core.settings import UserSettings


class BkResourceSettings(UserSettings):
    """
    Settings
    """

    DEFAULT_SETTINGS = defaultdict(
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


bk_resource_settings = BkResourceSettings("BK_RESOURCE")
