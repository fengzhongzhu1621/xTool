"""
Django settings for apps project.

Generated by 'django-admin startproject' using Django 3.2.15.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/3.2/ref/settings/
"""

import os
import sys

import environ
import pymysql
import urllib3
from django.db.backends.mysql.features import DatabaseFeatures
from django.utils.functional import cached_property
########################################################################################################################
# 兼容性处理
# django 3.2 默认的 default_auto_field 是 BigAutoField，django_celery_beat 在 2.2.1 版本已处理此问题
# 受限于 celery 和 bamboo 的版本，这里暂时这样手动设置 default_auto_field 来处理此问题
from django_celery_beat.apps import AppConfig

from core.load_settings import load_settings

AppConfig.default_auto_field = "django.db.models.AutoField"


# Patch the SSL module for compatibility with legacy CA credentials.
# https://stackoverflow.com/questions/72479812/how-to-change-tweak-python-3-10-default-ssl-settings-for-requests-sslv3-alert
urllib3.util.ssl_.DEFAULT_CIPHERS = "ALL:@SECLEVEL=1"


class PatchFeatures:
    @cached_property
    def minimum_database_version(self):
        if self.connection.mysql_is_mariadb:
            return 10, 4
        return 5, 6


# Django 4.2+ 不再官方支持 Mysql 5.7，但目前 Django 仅是对 5.7 做了软性的不兼容改动，
# 在没有使用 8.0 特异的功能时，对 5.7 版本的使用无影响，为兼容存量的 Mysql 5.7 DB 做此 Patch
DatabaseFeatures.minimum_database_version = PatchFeatures.minimum_database_version  # noqa

pymysql.install_as_MySQLdb()


########################################################################################################################
# 读取环境变量文件
# 配置优先级 环境变量 -> .env文件 -> settings.py
environ.Env.read_env()

ENVIRONMENT = os.getenv("ENVIRONMENT", "dev")
DJANGO_CONF_MODULE = "config.{env}".format(env=ENVIRONMENT)
try:
    _module = __import__(DJANGO_CONF_MODULE, globals(), locals(), ["*"])
except ImportError as e:
    raise ImportError("Could not import config '{}' (Is it on sys.path?): {}".format(DJANGO_CONF_MODULE, e))

for _setting in dir(_module):
    if _setting == _setting.upper():
        locals()[_setting] = getattr(_module, _setting)

# Build paths inside the project like this: BASE_DIR / 'subdir'.
# BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/3.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "django-insecure-*!%)j#u)nk*s+7!tm6uqw*l)q+q++b9wctsdic#hq3pp(_*&*7"

# 入口配置
ROOT_URLCONF = "apps.urls"
WSGI_APPLICATION = "apps.wsgi.application"
ASGI_APPLICATION = "apps.asgi.application"

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))

# 平台错误码前缀
PLATFORM_CODE = 00

SETTINGS_FOR_MERGE = ["INSTALLED_APPS", "MIDDLEWARE"]
MIDDLEWARE = []
INSTALLED_APPS = []

try:
    from config.celery_config import app  # noqa
except ImportError:
    pass

########################################################################################################################
# 多模块配置
base_dir = os.path.dirname(__file__)
DEPLOY_ALL_MODULE = "__all__"
DEPLOY_MODULE_ENV_KEY = "BKAPP_DEPLOY_MODULE"
MODULE_PATH = "modules"
DEFAULT_DEPLOY_MODULE = "default"
# 获取所有的模块
ALL_MODULES = [
    _path
    for _path in os.listdir(os.path.join(base_dir, MODULE_PATH))
    if not _path.startswith("_") and os.path.isdir(os.path.join(base_dir, MODULE_PATH, _path))
]
# 默认运行所有模块，根据环境变量运行
if os.getenv(DEPLOY_MODULE_ENV_KEY) == DEPLOY_ALL_MODULE:
    DEPLOY_MODULE = ALL_MODULES
else:
    DEPLOY_MODULE = [
        _module
        for _module in os.getenv(DEPLOY_MODULE_ENV_KEY, DEFAULT_DEPLOY_MODULE).split(",")
        if _module in ALL_MODULES
    ]

########################################################################################################################
# 添加运行 Path
sys.path.append(os.path.join(base_dir, "apps"))
sys.path.append(os.path.join(base_dir, MODULE_PATH))
for _module in DEPLOY_MODULE:
    sys.path.append(os.path.join(base_dir, f"{MODULE_PATH}/{_module}"))


########################################################################################################################
# 根据环境变量加载对应的配置文件
DJANGO_CONF_MODULE = "config.{env}".format(env=ENVIRONMENT)
locals().update(
    load_settings(
        DJANGO_CONF_MODULE, settings_for_merge={_setting: globals()[_setting] for _setting in SETTINGS_FOR_MERGE}
    )
)

########################################################################################################################
# 加载多模块的配置文件
for _module in DEPLOY_MODULE:
    module_path = f"{MODULE_PATH}.{_module}.settings"
    locals().update(
        load_settings(
            module_path, settings_for_merge={_setting: globals()[_setting] for _setting in SETTINGS_FOR_MERGE}
        )
    )
