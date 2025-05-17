import os

from config import APP_CODE

USE_REDIS = True

REDIS_HOST = os.environ.get("REDIS_HOST", "localhost")
REDIS_PORT = int(os.environ.get("REDIS_PORT", 6379))
REDIS_PASSWORD = os.environ.get("REDIS_PASSWORD")
REDIS_VERSION = int(os.environ.get("REDIS_VERSION", 2))
REDIS_KEY_PREFIX = os.environ.get("REDIS_KEY_PREFIX", APP_CODE)
REDIS_DB = os.getenv("REDIS_DB", "0")
REDIS_SENTINEL_PASSWORD = os.environ.get("BKAPP_REDIS_SENTINEL_PASSWORD", REDIS_PASSWORD)
REDIS_SERVICE_NAME = os.environ.get("BKAPP_REDIS_SERVICE_NAME", "mymaster")
replication_redis_cache = {
    "BACKEND": "django_redis.cache.RedisCache",
    "LOCATION": "{}/{}:{}/{}".format(REDIS_SERVICE_NAME, REDIS_HOST, REDIS_PORT, REDIS_DB),
    "OPTIONS": {
        "CLIENT_CLASS": "django_redis.client.SentinelClient",
        "PASSWORD": REDIS_PASSWORD,
        "SENTINEL_PASSWORD": REDIS_SENTINEL_PASSWORD,
    },
    "KEY_PREFIX": REDIS_KEY_PREFIX,
    "VERSION": REDIS_VERSION,
}
single_redis_cache = {
    "BACKEND": "django_redis.cache.RedisCache",  # 使用 django-redis 作为缓存后端
    "LOCATION": f"redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}",
    "OPTIONS": {
        "CLIENT_CLASS": "django_redis.client.DefaultClient",  # 使用默认的客户端类
        "REDIS_CLIENT_CLASS": "redis.client.StrictRedis",  # 使用 StrictRedis 客户端类
        "REDIS_CLIENT_KWARGS": {"decode_responses": True},  # 自动解码响应为字符串
        "SERIALIZER": "core.json.RedisJSONSerializer",  # 使用自定义的 JSON 序列化器
        "MAX_ENTRIES": 100000,  # 缓存的最大条目数
        "CULL_FREQUENCY": 10,  # 当缓存达到最大条目数时，保留 1/10 的数据
        "PASSWORD": REDIS_PASSWORD,
    },
    "KEY_PREFIX": REDIS_KEY_PREFIX,
    "VERSION": REDIS_VERSION,
}
REDIS_MODE = os.environ.get("BKAPP_REDIS_MODE", "single")
CACHES_GETTER = {"replication": replication_redis_cache, "single": single_redis_cache}
# 缓存设置
# CACHES = {
#     "db": {"BACKEND": "django.core.cache.backends.db.DatabaseCache", "LOCATION": "django_cache"},
#     "login_db": {"BACKEND": "django.core.cache.backends.db.DatabaseCache", "LOCATION": "account_cache"},
#     "dummy": {"BACKEND": "django.core.cache.backends.dummy.DummyCache"},
#     "locmem": {"BACKEND": "django.core.cache.backends.locmem.LocMemCache"},
# }
CACHES = {
    "db": {
        "BACKEND": "django.core.cache.backends.db.DatabaseCache",
        "LOCATION": "django_cache",
        "OPTIONS": {"MAX_ENTRIES": 100000, "CULL_FREQUENCY": 10},
    },
    "login_db": CACHES_GETTER[REDIS_MODE],
    "dummy": {"BACKEND": "django.core.cache.backends.dummy.DummyCache"},
    "locmem": {"BACKEND": "django.core.cache.backends.locmem.LocMemCache"},
    "default": CACHES_GETTER[REDIS_MODE],
}
DATA_BACKEND_REDIS_MODE = os.environ.get("BKAPP_DATA_BACKEND_REDIS_MODE", "single")
DATA_BACKEND = "apps.backend.data.redis_backend.RedisDataBackend"
if USE_REDIS:
    CACHES["redis"] = CACHES_GETTER[REDIS_MODE]
    CACHES["default"] = CACHES["redis"]
    CACHES["login_db"] = CACHES["redis"]  # 登录数据库缓存
else:
    CACHES["default"] = CACHES["db"]

# CACHES["login_db"] = {  # 定义名为 'login_db' 的第二个缓存
#     "BACKEND": "django.core.cache.backends.db.DatabaseCache",  # 使用数据库作为缓存后端
#     "LOCATION": "account_cache",  # 使用名为 'account_cache' 的数据库表
# }

# 登录缓存时间配置, 单位秒（与django cache单位一致）
LOGIN_CACHE_EXPIRED = int(os.getenv("LOGIN_CACHE_EXPIRED", 60))

DJANGO_REDIS_CONNECTION_FACTORY = "core.redis.ConnectionFactory"
