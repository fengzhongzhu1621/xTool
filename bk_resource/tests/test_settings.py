from bk_resource.settings import bk_resource_settings


class TestBkResourceSettings:
    def test_get(self):
        assert bk_resource_settings.DEFAULT_API_DIR == "api"
        assert bk_resource_settings.DEFAULT_RESOURCE_DIRS == []
        assert bk_resource_settings.DEFAULT_ERROR_RESPONSE_SERIALIZER.__name__ == "ErrorResponseSerializer"
        assert bk_resource_settings.DEFAULT_PAGINATOR_RESPONSE_BUILDER.__name__ == "PaginatorResponseBuilder"
        assert bk_resource_settings.DEFAULT_STANDARD_RESPONSE_BUILDER.__name__ == "StandardResponseBuilder"
        assert bk_resource_settings.DEFAULT_SWAGGER_SCHEMA_CLASS.__name__ == "BkResourceSwaggerAutoSchema"
        assert bk_resource_settings.REQUEST_LOG_HANDLER.__name__ == "RequestLogHandler"
