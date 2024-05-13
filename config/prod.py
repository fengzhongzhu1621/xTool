from config import RUN_VER

if RUN_VER == "open":
    # pylint: disable=wildcard-import
    from blueapps.patch.settings_open_saas import *  # noqa
else:
    from blueapps.patch.settings_paas_services import *  # pylint: disable=wildcard-import # noqa

# 正式环境
RUN_MODE = "PRODUCT"

# 只对正式环境日志级别进行配置，可以在这里修改
LOG_LEVEL = "ERROR"


# 正式环境数据库可以在这里配置
# DATABASES.update(
#     {
#         # 外部数据库授权，请联系 【蓝鲸助手】
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
