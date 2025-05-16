import os

from .language import TIME_ZONE

# celery 配置
# CELERY 开关，使用时请改为 True，修改项目目录下的 Procfile 文件，添加以下两行命令：
# worker: python manage.py celery worker -l info
# beat: python manage.py celery beat -l info
# 不使用时，请修改为 False，并删除项目目录下的 Procfile 文件中 celery 配置
# 下面的命令用于测试
# python manage.py celery worker -O fair -l info -c 1 -Q celery,default,er_schedule,er_execute
IS_USE_CELERY = True

# Rabbitmq & Celery
if "RABBITMQ_VHOST" in os.environ:
    RABBITMQ_VHOST = os.getenv("RABBITMQ_VHOST")
    RABBITMQ_PORT = os.getenv("RABBITMQ_PORT")
    RABBITMQ_HOST = os.getenv("RABBITMQ_HOST")
    RABBITMQ_USER = os.getenv("RABBITMQ_USER")
    RABBITMQ_PASSWORD = os.getenv("RABBITMQ_PASSWORD")
    BROKER_URL = "amqp://{user}:{password}@{host}:{port}/{vhost}".format(
        user=RABBITMQ_USER,
        password=RABBITMQ_PASSWORD,
        host=RABBITMQ_HOST,
        port=RABBITMQ_PORT,
        vhost=RABBITMQ_VHOST,
    )

CELERYD_HIJACK_ROOT_LOGGER = False
# CELERY与RabbitMQ增加60秒心跳设置项
BROKER_HEARTBEAT = 60
# celery settings
if IS_USE_CELERY:
    INSTALLED_APPS = (
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
    CELERY_TIMEZONE = TIME_ZONE
    CELERYBEAT_SCHEDULER = "django_celery_beat.schedulers:DatabaseScheduler"
    # 允许传递对象给任务
    CELERY_TASK_SERIALIZER = "json"
    CELERY_ACCEPT_CONTENT = ["json"]
    # CELERY 任务的文件路径，即包含有 @task 装饰器的函数文件
    CELERY_IMPORTS = []
