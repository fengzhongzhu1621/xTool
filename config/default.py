# pylint: disable=wildcard-import

from blueapps.conf.default_settings import *  # noqa
from celery.utils.serialization import strtobool

from config.log import get_logging_config_dict

INIT_SUPERUSER = []

ALLOWED_HOSTS = []

# Application definition

INSTALLED_APPS = (
    "bkoauth",
    # 框架自定义命令
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.sites",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # account app
    "blueapps.account",
    "rest_framework",
    "bk_resource",
    "drf_yasg",
    "version_log",
    "apps.core.drf_resource",
    # "apigw_manager.apigw",
    # bamboo-pipeline
    # "pipeline",
    # "pipeline.django_signal_valve",
    # "pipeline.log",
    # "pipeline.engine",
    # "pipeline.component_framework",
    # "pipeline.variable_framework",
    # "pipeline.eri",
    # "pipeline.contrib.engine_admin",
    # 业务逻辑
    "apps.backend",
    "apps.entry",
    # "apps.quickstart",
    # "apps.snippets",
    "apps.custom_plugins",
    "apps.credential",
    "apps.global_conf",
    "apps.http_client",
    "apps.version",
    "apps.opentelemetry_instrument",
)

MIDDLEWARE = (
    # 将请求对象注入到线程变量，方便根据 get_request() 方法获取
    "apps.core.middleware.RequestProvider",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.security.SecurityMiddleware",
    # 蓝鲸静态资源服务
    "whitenoise.middleware.WhiteNoiseMiddleware",
    # Auth middleware
    # "blueapps.account.middlewares.RioLoginRequiredMiddleware",
    # "blueapps.account.middlewares.WeixinLoginRequiredMiddleware",
    # "blueapps.account.middlewares.LoginRequiredMiddleware",
    # exception middleware
    "apps.core.middleware.AppExceptionMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    # "apigw_manager.apigw.authentication.ApiGatewayJWTGenericMiddleware",  # JWT 认证
    # "apigw_manager.apigw.authentication.ApiGatewayJWTAppMiddleware",  # JWT 透传的应用信息
    # "apigw_manager.apigw.authentication.ApiGatewayJWTUserMiddleware",  # JWT 透传的用户信息
    "corsheaders.middleware.CorsMiddleware",
    "core.middleware.csrf.CSRFExemptMiddleware",
)

AUTHENTICATION_BACKENDS = ("django.contrib.auth.backends.ModelBackend",)
# AUTHENTICATION_BACKENDS += ("apigw_manager.apigw.authentication.UserModelBackend",)

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

# Password validation
# https://docs.djangoproject.com/en/3.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

# Internationalization
# https://docs.djangoproject.com/en/3.2/topics/i18n/
# 国际化配置
LOCALE_PATHS = (os.path.join(BASE_DIR, "locale"),)  # noqa

# 时区
USE_I18N = True
USE_TZ = True
TIME_ZONE = "Asia/Shanghai"
# TIME_ZONE = "UTC"
LANGUAGE_CODE = "zh-hans"
# LANGUAGE_CODE = "en-us"
LANGUAGES = (
    ("en", "English"),
    ("zh-hans", "简体中文"),
)
LANGUAGE_COOKIE_NAME = os.getenv("BKAPP_LANGUAGE_COOKIE_NAME", "blueking_language")

# Default primary key field type
# https://docs.djangoproject.com/en/3.2/ref/settings/#default-auto-field
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# 所有环境的日志级别可以在这里配置
# LOG_LEVEL = 'INFO'

# 静态资源文件(js,css等）在APP上线更新后, 由于浏览器有缓存,
# 可能会造成没更新的情况. 所以在引用静态资源的地方，都把这个加上
# Django 模板中：<script src="/a.js?v=${STATIC_VERSION}"></script>
# 如果静态资源修改了以后，上线前改这个版本号即可
STATIC_VERSION = "1.0"

STATICFILES_DIRS = [os.path.join(BASE_DIR, "static")]  # noqa

MEDIA_ROOT = os.path.join(BASE_DIR, "media")

REST_FRAMEWORK = {
    "EXCEPTION_HANDLER": "apps.core.exception.custom_exception_handler",
    "DEFAULT_PERMISSION_CLASSES": ("rest_framework.permissions.IsAuthenticated",),
    "DEFAULT_PAGINATION_CLASS": "apps.core.drf.pagination.CustomPageNumberWithColumnPagination",
    "PAGE_SIZE": 10,
    "TEST_REQUEST_DEFAULT_FORMAT": "json",
    "DEFAULT_AUTHENTICATION_CLASSES": ("rest_framework.authentication.SessionAuthentication",),
    "DEFAULT_FILTER_BACKENDS": ("django_filters.rest_framework.DjangoFilterBackend",),
    "DATETIME_FORMAT": "%Y-%m-%d %H:%M:%S",
    "NON_FIELD_ERRORS_KEY": "params_error",
    "DEFAULT_PARSER_CLASSES": (
        "rest_framework.parsers.JSONParser",
        "rest_framework.parsers.MultiPartParser",
    ),
    "DEFAULT_RENDERER_CLASSES": ("apps.core.drf.renderers.APIRenderer",),
    # 版本管理
    "DEFAULT_VERSIONING_CLASS": "rest_framework.versioning.URLPathVersioning",
    "DEFAULT_VERSION": "v1",
    "ALLOWED_VERSIONS": ["v1"],
    "VERSION_PARAM": "version",
}

# 前后端分离开发配置开关，设置为True时dev和stag环境会自动加载允许跨域的相关选项
FRONTEND_BACKEND_SEPARATION = False

# load logging settings
LOGGING = get_logging_config_dict(locals())

# BKUI是否使用了history模式
IS_BKUI_HISTORY_MODE = False

# 是否需要对AJAX弹窗登录强行打开
IS_AJAX_PLAIN_MODE = False

# BkResource - Platform
PLATFORM = os.getenv("BKPAAS_ENGINE_REGION")

# BkResource
SWAGGER_SETTINGS = {
    "DEFAULT_INFO": "urls.info",
    "DEFAULT_GENERATOR_CLASS": "bk_resource.utils.generators.BKResourceOpenAPISchemaGenerator",
}
BK_RESOURCE = {
    "REQUEST_VERIFY": strtobool(os.getenv("BKAPP_API_REQUEST_VERIFY", "False")),
    "REQUEST_LOG_SPLIT_LENGTH": int(os.getenv("BKAPP_REQUEST_LOG_SPLIT_LENGTH", 1024)),
    "PLATFORM_AUTH_ENABLED": strtobool(os.getenv("BKAPP_PLATFORM_AUTH_ENABLED", "False")),
    "PLATFORM_AUTH_ACCESS_TOKEN": os.getenv("BKAPP_PLATFORM_AUTH_ACCESS_TOKEN"),
    "PLATFORM_AUTH_ACCESS_USERNAME": os.getenv("BKAPP_PLATFORM_AUTH_ACCESS_USERNAME"),
}
BK_BK_RESOURCE_LOG_ENABLED = strtobool(os.getenv("BKAPP_BK_RESOURCE_LOG_ENABLED", "true"))
if BK_BK_RESOURCE_LOG_ENABLED:
    LOGGING["loggers"]["bk_resource"] = LOGGING["loggers"]["app"]
    LOGGING["loggers"]["iam"] = LOGGING["loggers"]["app"]

# CORS
SESSION_COOKIE_DOMAIN = os.getenv("BKAPP_SESSION_COOKIE_DOMAIN")
CSRF_COOKIE_DOMAIN = os.getenv("BKAPP_CSRF_COOKIE_DOMAIN", SESSION_COOKIE_DOMAIN)
LANGUAGE_COOKIE_DOMAIN = SESSION_COOKIE_DOMAIN
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOWED_ORIGINS = [origin for origin in str(os.getenv("BKAPP_CORS_ALLOWED_ORIGINS", "")).split(",") if origin]

# CSRF
CSRF_TRUSTED_ORIGINS = [origin for origin in str(os.getenv("BKAPP_CSRF_TRUSTED_ORIGINS", "")).split(",") if origin]
CSRF_EXEMPT_PATHS = []

# UserCookie
AUTH_BACKEND_DOMAIN = os.getenv("BKAPP_AUTH_BACKEND_DOMAIN", SESSION_COOKIE_DOMAIN)
AUTH_BACKEND_TYPE = os.getenv("BKAPP_AUTH_BACKEND_TYPE", "bk_token")
OAUTH_COOKIES_PARAMS = {AUTH_BACKEND_TYPE: AUTH_BACKEND_TYPE}

# redis
USE_REDIS = True
REDIS_HOST = os.environ.get("REDIS_HOST", "localhost")
REDIS_PORT = int(os.environ.get("REDIS_PORT", 6379))
REDIS_PASSWORD = os.environ.get("REDIS_PASSWORD")
REDIS_VERSION = int(os.environ.get("REDIS_VERSION", 2))
REDIS_KEY_PREFIX = os.environ.get("REDIS_KEY_PREFIX")
REDIS_DB = os.getenv("REDIS_DB", "0")
REDIS_SENTINEL_PASSWORD = os.environ.get("BKAPP_REDIS_SENTINEL_PASSWORD", REDIS_PASSWORD)
REDIS_SERVICE_NAME = os.environ.get("BKAPP_REDIS_SERVICE_NAME", "mymaster")
replication_redis_cache = {
    "BACKEND": "django_redis.cache.RedisCache",
    "LOCATION": "{}/{}:{}/{}".format(REDIS_SERVICE_NAME, REDIS_HOST, REDIS_PORT, REDIS_DB),
    "OPTIONS": {
        "CLIENT_CLASS": "django_redis.client.SentinelClient",
        "PASSWORD": REDIS_PASSWORD,
        "SENTINEL_PASSWORD": REDIS_SENTINEL_PASSWORD,
    },
    "KEY_PREFIX": REDIS_KEY_PREFIX,
    "VERSION": REDIS_VERSION,
}
single_redis_cache = {
    "BACKEND": "django_redis.cache.RedisCache",
    "LOCATION": f"redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}",
    "OPTIONS": {"CLIENT_CLASS": "django_redis.client.DefaultClient", "PASSWORD": REDIS_PASSWORD},
    "KEY_PREFIX": REDIS_KEY_PREFIX,
    "VERSION": REDIS_VERSION,
}
REDIS_MODE = os.environ.get("BKAPP_REDIS_MODE", "single")
CACHES_GETTER = {"replication": replication_redis_cache, "single": single_redis_cache}

# 数据库
DATABASES["default"].setdefault("OPTIONS", {})["charset"] = "utf8mb4"

# CELERY 开关，使用时请改为 True，修改项目目录下的 Procfile 文件，添加以下两行命令：
# worker: python manage.py celery worker -l info
# beat: python manage.py celery beat -l info
# 不使用时，请修改为 False，并删除项目目录下的 Procfile 文件中 celery 配置
# 下面的命令用于测试
# python manage.py celery worker -O fair -l info -c 1 -Q celery,default,er_schedule,er_execute
IS_USE_CELERY = True

# celery settings
if IS_USE_CELERY:
    INSTALLED_APPS = locals().get("INSTALLED_APPS", [])
    INSTALLED_APPS += (
        "django_celery_beat",
        "django_celery_results",
    )

    # 用于替换默认的队列
    if os.getenv("BK_BROKER_URL"):
        BROKER_URL = os.getenv("BK_BROKER_URL")

    # CELERY 并发数，默认为 2，是命令行-c参数指定的数目，可以通过环境变量或者 Procfile 设置
    CELERYD_CONCURRENCY = os.getenv("BK_CELERYD_CONCURRENCY", 2)  # noqa
    # celery beat 间隔时间，默认为 1，是命令行-B参数指定的数目，可以通过环境变量或者 Procfile 设置
    CELERY_ENABLE_UTC = True
    CELERYBEAT_SCHEDULER = "django_celery_beat.schedulers:DatabaseScheduler"
    # 允许传递对象给任务
    CELERY_TASK_SERIALIZER = "json"
    CELERY_ACCEPT_CONTENT = ["json"]
    # CELERY 任务的文件路径，即包含有 @task 装饰器的函数文件
    CELERY_IMPORTS = []

# 分页最大限制
MAX_PAGE_SIZE = int(os.getenv("BKAPP_MAX_PAGE_SIZE", 1000))
# 数据库分配最大限制
DB_BATCH_SIZE = int(os.getenv("BKAPP_DB_BATCH_SIZE", 1000))

# 缓存设置
CACHES["redis"] = CACHES_GETTER[REDIS_MODE]
CACHES["default"] = CACHES["redis"]
# session 存储后端
CACHES["login_db"] = CACHES["redis"]
DATA_BACKEND_REDIS_MODE = os.environ.get("BKAPP_DATA_BACKEND_REDIS_MODE", "single")
DATA_BACKEND = "apps.backend.data.redis_backend.RedisDataBackend"

# OpenTelemetry
OPEN_TELEMETRY_ENABLE_OTEL_METRICS = bool(strtobool(os.getenv("OPEN_TELEMETRY_ENABLE_OTEL_METRICS", "False")))
OPEN_TELEMETRY_ENABLE_OTEL_TRACE = bool(strtobool(os.getenv("OPEN_TELEMETRY_ENABLE_OTEL_TRACE", "False")))
OPEN_TELEMETRY_OTEL_INSTRUMENT_DB_API = bool(strtobool(os.getenv("OPEN_TELEMETRY_OTEL_INSTRUMENT_DB_API", "False")))
OPEN_TELEMETRY_OTEL_SERVICE_NAME = os.getenv("OPEN_TELEMETRY_OTEL_SERVICE_NAME") or APP_CODE

OPEN_TELEMETRY_OTEL_ADDTIONAL_INSTRUMENTORS = []
OPEN_TELEMETRY_OTEL_LOGGING_TRACE_FORMAT = (
    "[trace_id]: %(otelTraceID)s [span_id]: %(otelSpanID)s [resource.service.name]: %(otelServiceName)s"
)


# 本机地址
BK_HOST = os.getenv("BKAPP_HOST", "")

# 流程component自动注册目录
COMPONENT_PATH = []

# pipeline
LOG_PERSISTENT_DAYS = 30  # 设置引擎日志的有效期

# 唯一随机串生成重试次数
RANDOM_STR_GENERATE_REPEAT_TIMES = 3

# remove disabled apps
if locals().get("DISABLED_APPS"):
    INSTALLED_APPS = locals().get("INSTALLED_APPS", [])
    DISABLED_APPS = locals().get("DISABLED_APPS", [])

    INSTALLED_APPS = [_app for _app in INSTALLED_APPS if _app not in DISABLED_APPS]

    _keys = (
        "AUTHENTICATION_BACKENDS",
        "DATABASE_ROUTERS",
        "FILE_UPLOAD_HANDLERS",
        "MIDDLEWARE",
        "PASSWORD_HASHERS",
        "TEMPLATE_LOADERS",
        "STATICFILES_FINDERS",
        "TEMPLATE_CONTEXT_PROCESSORS",
    )

    import itertools

    for _app, _key in itertools.product(DISABLED_APPS, _keys):
        if locals().get(_key) is None:
            continue
        locals()[_key] = tuple([_item for _item in locals()[_key] if not _item.startswith(_app + ".")])
