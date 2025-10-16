import os
from distutils.util import strtobool

INSTALLED_APPS = [
    "bk_resource",
]

# BkResource - Platform
PLATFORM = os.getenv("BKPAAS_ENGINE_REGION")

BKAPP_RESOURCE_DEBUG = strtobool(os.getenv("BKAPP_RESOURCE_DEBUG", "False"))

BK_RESOURCE = {
    "REQUEST_VERIFY": strtobool(os.getenv("BKAPP_API_REQUEST_VERIFY", "False")),
    "REQUEST_LOG_SPLIT_LENGTH": int(os.getenv("BKAPP_REQUEST_LOG_SPLIT_LENGTH", 1024)),  # 请求日志截断长度，0表示不截断
    "PLATFORM_AUTH_ENABLED": True,
    "PLATFORM_AUTH_ACCESS_TOKEN": os.getenv("BKAPP_PLATFORM_AUTH_ACCESS_TOKEN"),
    "PLATFORM_AUTH_ACCESS_USERNAME": os.getenv("BKAPP_PLATFORM_AUTH_ACCESS_USERNAME", "admin"),
    "RESOURCE_BULK_REQUEST_PROCESSES": os.getenv("BKAPP_RESOURCE_BULK_REQUEST_PROCESSES"),
}
SWAGGER_SETTINGS = {
    "DEFAULT_INFO": "urls.info",
    "DEFAULT_GENERATOR_CLASS": "bk_resource.utils.generators.BKResourceOpenAPISchemaGenerator",
}
