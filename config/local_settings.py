# -*- coding: utf-8 -*-

# celery本地执行，方便调试
CELERY_TASK_ALWAYS_EAGER = True
CELERY_ALWAYS_EAGER = True
CELERY_EAGER_PROPAGATES_EXCEPTIONS = True
CELERY_TASK_EAGER_PROPAGATES = True
CELERY_EAGER_PROPAGATES = True

REDIS_CELERY_CONF = {
    "host": "localhost",
    "port": "6379",
    "db": 0,
    "password": "",
}
