import logging
import sys

from config.sub_config.log import get_logging_config_dict

DEBUG_RETURN_EXCEPTION = True

SQL_TABLE_IGNORE_LIST = [
    "account_cache",
    "account_user",
    "account_user_groups",
    "account_user_property",
    "account_user_user_permissions",
    "account_verifyinfo",
    "auth_group",
    "auth_group_permissions",
    "auth_permission",
    "bkoauth_access_token",
    "django_admin_log",
    "django_cache",
    "django_content_type",
    "django_migrations",
    "django_session",
    "django_site",
]

SQL_IGNORE_LIST = [
    "TRUNCATE",
    "SAVEPOINT",
    "RELEASE SAVEPOINT",
    "SET FOREIGN_KEY_CHECKS",
    "SHOW FULL TABLES",
    "SELECT @@SQL_AUTO_IS_NULL",
    "SELECT VERSION()",
    "SET SESSION TRANSACTION ISOLATION LEVEL",
    "SELECT ENGINE FROM INFORMATION_SCHEMA.ENGINES",
]


class SQLFilter(logging.Filter):
    def filter(self, record):
        """
        Determine if the specified record is to be logged.

        Is the specified record to be logged? Returns 0 for no, nonzero for
        yes. If deemed appropriate, the record may be modified in-place.
        """
        if hasattr(record, "sql"):
            sql = record.sql
            if sql:
                for table_name in SQL_TABLE_IGNORE_LIST:
                    if "`{}`".format(table_name) in record.sql:
                        return False
                for sql in SQL_IGNORE_LIST:
                    if sql in record.sql:
                        return False
        return True


IS_LOCAL = True


# load logging settings
LOG_TIME_FORMAT = "%Y-%m-%d %H:%M:%S.%f"
LOGGING = get_logging_config_dict(locals())
LOGGING["loggers"]["app"] = {"handlers": ["console"], "level": "DEBUG", "propagate": True}
LOGGING["loggers"]["django.db.backends"] = {"handlers": ["console"], "level": "DEBUG", "propagate": False}
LOGGING["loggers"]["bk_resource"] = LOGGING["loggers"]["app"]
LOGGING["loggers"]["bk_audit"] = LOGGING["loggers"]["app"]
LOGGING["loggers"]["iam"] = LOGGING["loggers"]["app"]
LOGGING["handlers"]["console"]["filters"] = ["sql_filter"]
LOGGING["filters"] = {
    "sql_filter": {
        "()": SQLFilter,
        "name": "sql_filter",
    }
}
for _l in LOGGING["loggers"].values():
    _l["propagate"] = False

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": "db_test_xtool",  # 数据库名
        "USER": "root",
        "PASSWORD": "",
        "HOST": "localhost",
        "PORT": "3306",
        "OPTIONS": {"init_command": "SET default_storage_engine=INNODB", "charset": "utf8mb4"},
        "TEST": {
            "name": "db_test_xtool",
            "CHARSET": "utf8mb4",
        },
    },
}

OPEN_TELEMETRY_ENABLE_OTEL_METRICS = True
OPEN_TELEMETRY_ENABLE_OTEL_TRACE = True
OPEN_TELEMETRY_OTEL_INSTRUMENT_DB_API = True

# 启动登录详细概略获取(通过调用api获取ip详细地址。如果是内网，关闭即可)
ENABLE_LOGIN_ANALYSIS_LOG = True
# 登录接口 /api/token/ 是否需要验证码认证，用于测试，正式环境建议取消
LOGIN_NO_CAPTCHA_AUTH = True
# 列权限中排除App应用
COLUMN_EXCLUDE_APPS = []
# 开启 IP 分析
ENABLE_LOGIN_ANALYSIS_LOG = True

BROKER_URL = "redis://localhost:6379/0"

iam_logger = logging.getLogger("iam")
iam_logger.setLevel(logging.DEBUG)

debug_handler = logging.StreamHandler(sys.stdout)
debug_handler.setFormatter(logging.Formatter('%(levelname)s [%(asctime)s] [IAM] %(message)s'))
iam_logger.addHandler(debug_handler)
