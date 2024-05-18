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

ENABLE_OTEL_METRICS = True
