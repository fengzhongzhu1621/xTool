import os

from core.load_settings import load_settings

# 判断是否为本地开发环境
IS_LOCAL = not os.getenv("ENVIRONMENT", False)

SITE_ID = 1

########################################################################################################################
# Application definition
INSTALLED_APPS = (
    # "bkoauth",
    # 框架自定义命令
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.sites",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "apps.opentelemetry_instrument",
    "rest_framework",
    "django_dbconn_retry",
    "drf_yasg",
    # 一定要把debug_toolbar放在django.contrib.staticfiles后面
    "debug_toolbar",
    # "bk_resource",
    "captcha",
    "channels",
    "apps.account",
    "version_log",
    "core.drf_resource",
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
    "apps.version",
    "apps.entry",
    "apps.backend",
    # "apps.quickstart",
    # "apps.snippets",
    "apps.credential",
    "apps.global_conf",
    "apps.http_client",
    "apps.websocket",
    "apps.periodic_task",
)

########################################################################################################################
MIDDLEWARE = (
    # 跨域中间件
    "corsheaders.middleware.CorsMiddleware",
    # 接口耗时调试工具
    "pyinstrument.middleware.ProfilerMiddleware",
    "core.middleware.healthz.HealthCheckMiddleware",
    # 分析页面、接口和SQL调用耗时调试工具
    "debug_toolbar.middleware.DebugToolbarMiddleware",
    # 将请求对象注入到线程变量，方便根据 get_request() 方法获取
    "core.middleware.request_provider.RequestProvider",
    # default
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    # Auth middleware
    # exception middleware
    "core.middleware.app_exception.AppExceptionMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "core.csrf.middleware.CSRFExemptMiddleware",
    "core.csrf.middleware.DisableCSRFCheckMiddleware",
    "apps.account.middleware.ApiLoggingMiddleware",
)

########################################################################################################################
# vue
VUE_INDEX = "index.html"
# AUTHENTICATION_BACKENDS = ("django.contrib.auth.backends.ModelBackend",)
AUTHENTICATION_BACKENDS = ("core.auth.backends.Md5ModelBackend",)

# 前后端分离开发配置开关，设置为True时dev和stag环境会自动加载允许跨域的相关选项
FRONTEND_BACKEND_SEPARATION = False


# BKUI是否使用了history模式
IS_BKUI_HISTORY_MODE = False

# 是否需要对AJAX弹窗登录强行打开
IS_AJAX_PLAIN_MODE = True


########################################################################################################################
# 分页
MAX_PAGE_SIZE = int(os.getenv("BKAPP_MAX_PAGE_SIZE", 1000))

########################################################################################################################
# 流程
# 流程component自动注册目录
COMPONENT_PATH = []

# pipeline
LOG_PERSISTENT_DAYS = 30  # 设置引擎日志的有效期

# 唯一随机串生成重试次数
RANDOM_STR_GENERATE_REPEAT_TIMES = 3

# 是否开启 IP 分析
LOGIN_ANALYSIS_LOG_ENABLED = False

# 列权限需要排除的App应用
COLUMN_EXCLUDE_APPS = ["channels", "captcha"] + locals().get("COLUMN_EXCLUDE_APPS", [])

# channels
CHANNEL_LAYERS = {}

########################################################################################################################
# 加载第三方应用配置
SETTINGS_FOR_MERGE = ["INSTALLED_APPS", "MIDDLEWARE"]
for module_name in [
    "media",
    "static",
    "url",
    "template",
    "validation",
    "user",
    "language",
    "cookie",
    "session",
    "database",
    "csrf",
    "cors",
    "debug",
    "safety",
    "rest_framework",
    "pyinstrument",
    "bk_resource",
    "cache",
    "queue",
    "opentelemetry",
    "version_log",
]:
    locals().update(
        load_settings(
            f"config.sub_config.{module_name}",
            settings_for_merge={_setting: globals()[_setting] for _setting in SETTINGS_FOR_MERGE},
            raise_exception=True,
        )
    )


########################################################################################################################
# global_conf
FUNCTION_CONTROLLER_INIT_MAP = {
    "root": {
        "name": "root",
        "is_enabled": True,
        "children": {
            "user": {
                "name": "user",
                "is_enabled": True,
                "children": {
                    "create": {"name": "create", "is_enabled": True},
                    "delete": {"name": "delete", "is_enabled": False},
                },
            }
        },
    }
}

########################################################################################################################
# 其它
# 本机地址
BK_HOST = os.getenv("BKAPP_HOST", "")
# request_id 的头
REQUEST_ID_HEADER = "HTTP_X_REQUEST_ID"
# 并发
CONCURRENT_NUMBER = 10

USE_X_FORWARDED_HOST = True


########################################################################################################################
"""
以下为框架代码 请勿修改
"""
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
