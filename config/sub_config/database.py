import os
import sys


def get_default_database_config_dict(settings_module):
    if os.getenv("GCS_MYSQL_NAME") and os.getenv("MYSQL_NAME"):
        db_prefix = os.getenv("DB_PREFIX")
        if not db_prefix:
            sys.stderr.write(
                "Without DB_PREFIX environment variable while 'GCS_MYSQL_NAME' and 'MYSQL_NAME' are configured."
            )
            return {}
    elif os.getenv("GCS_MYSQL_NAME"):
        db_prefix = "GCS_MYSQL"
    elif os.getenv("MYSQL_NAME"):
        db_prefix = "MYSQL"
    else:
        if not settings_module.get("IS_LOCAL", False):
            # 对应非GCS_MYSQL或MYSQL开头的情况，需开发者自行配置
            sys.stderr.write("DB_PREFIX config is not 'GCS_MYSQL' or 'MYSQL_NAME'\n")
        return {}
    return {
        "ENGINE": "django.db.backends.mysql",
        "NAME": os.environ["%s_NAME" % db_prefix],
        "USER": os.environ["%s_USER" % db_prefix],
        "PASSWORD": os.environ["%s_PASSWORD" % db_prefix],
        "HOST": os.environ["%s_HOST" % db_prefix],
        "PORT": os.environ["%s_PORT" % db_prefix],
        "OPTIONS": {"isolation_level": "repeatable read"},
    }


DATABASES = {"default": get_default_database_config_dict(locals())}
DB_BATCH_SIZE = int(os.getenv("BKAPP_DB_BATCH_SIZE", 1000))
DATABASES["default"].setdefault("OPTIONS", {})["charset"] = "utf8mb4"
# DATABASE_ROUTERS = ["config.router.DatabaseRouter"]

# Default primary key field type
# https://docs.djangoproject.com/en/3.2/ref/settings/#default-auto-field
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# for django-dbconn-retry
MAX_DBCONN_RETRY_TIMES = 3
