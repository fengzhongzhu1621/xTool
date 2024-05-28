import pymysql

pymysql.install_as_MySQLdb()

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
