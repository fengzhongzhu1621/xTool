# pylint: disable=wildcard-import
from config.default import *  # noqa

# 预发布环境
RUN_MODE = "STAGING"

# 只对正式环境日志级别进行配置，可以在这里修改
LOG_LEVEL = "ERROR"

DEBUG_RETURN_EXCEPTION = False

STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"


# 正式环境数据库可以在这里配置
# DATABASES.update(
#     {
#         'external_db': {
#             'ENGINE': 'django.db.backends.mysql',
#             'NAME': '',  # 外部数据库名
#             'USER': '',  # 外部数据库用户
#             'PASSWORD': '',  # 外部数据库密码
#             'HOST': '',  # 外部数据库主机
#             'PORT': '',  # 外部数据库端口
#         },
#     }
# )
