# pylint: disable=wildcard-import
from config.default import *  # noqa

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

# 本地开发环境
RUN_MODE = "DEVELOP"

# APP本地静态资源目录
STATIC_URL = "/static/"

# APP静态资源目录url
REMOTE_STATIC_URL = "%sremote/" % STATIC_URL

# Celery 消息队列设置 RabbitMQ
# BROKER_URL = 'amqp://guest:guest@localhost:5672//'
# Celery 消息队列设置 Redis
BROKER_URL = "redis://localhost:6379/0"

DEBUG = True

try:
    MIDDLEWARE = tuple(["pyinstrument.middleware.ProfilerMiddleware"] + list(MIDDLEWARE))
except ImportError:
    pass  # 如果中间件不存在，忽略

# celery任务本地执行，方便测试和调试
CELERY_TASK_ALWAYS_EAGER = True
CELERY_ALWAYS_EAGER = True
CELERY_EAGER_PROPAGATES_EXCEPTIONS = True
CELERY_TASK_EAGER_PROPAGATES = True
CELERY_EAGER_PROPAGATES = True

# 本地开发数据库设置
# USE FOLLOWING SQL TO CREATE THE DATABASE NAMED APP_CODE
# SQL: CREATE DATABASE `db_test_xtool` DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci; # noqa: E501

REDIS_CELERY_CONF = {
    "host": "localhost",
    "port": "6379",
    "db": 0,
    "password": "",
}

# Database
# https://docs.djangoproject.com/en/3.2/ref/settings/#databases
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": "db_test_xtool",  # 数据库名
        "USER": "root",
        "PASSWORD": "",
        "HOST": "localhost",
        "PORT": "3306",
        "TEST": {
            "name": "db_test_xtool",
            "CHARSET": "utf8mb4",
        },
    },
}

# 用于替换默认的队列
BROKER_URL = os.getenv("BK_BROKER_URL", "redis://localhost:6379/0")
CELERY_RESULT_BACKEND = "redis://localhost:6379/0"

# 多人开发时，无法共享的本地配置可以放到新建的 local_settings.py 文件中
# 并且把 local_settings.py 加入版本管理忽略文件中
try:
    # pylint: disable=wildcard-import
    from .local_settings import *  # noqa
except ImportError:
    pass
