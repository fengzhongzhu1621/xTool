from django.conf import settings

from core.load_settings import load_settings

INSTALLED_APPS = ()

MIDDLEWARE = []

########################################################################################################################
# 加载第三方应用配置
SETTINGS_FOR_MERGE = ["INSTALLED_APPS", "MIDDLEWARE"]
for module_name in ["vision"]:
    locals().update(
        load_settings(
            f"modules.default.config.{module_name}",
            settings_for_merge={_setting: globals()[_setting] for _setting in SETTINGS_FOR_MERGE},
            raise_exception=True,
        )
    )

if settings.IS_USE_CELERY:
    # CELERY 配置，申明任务的文件路径，即包含有 @task 装饰器的函数文件
    CELERY_IMPORTS = ()
    CELERYBEAT_SCHEDULE = {}
