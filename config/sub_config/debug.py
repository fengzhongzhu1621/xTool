import os

from celery.utils.serialization import strtobool

DEBUG_RETURN_EXCEPTION = False

DEBUG_TOOL_BAR = strtobool(os.getenv("DEBUG_TOOL_BAR", "False"))


# for django debug toolbar
# 只有访问这里面配置的ip地址时， Debug Toolbar才是展示出来
INTERNAL_IPS = ["127.0.0.1", "localhost"]
