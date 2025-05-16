import os

from config import BASE_DIR

# Internationalization
# https://docs.djangoproject.com/en/3.2/topics/i18n/
# 国际化配置
LOCALE_PATHS = (os.path.join(BASE_DIR, "locale"),)  # noqa

# 时区
USE_I18N = True
USE_TZ = True
TIME_ZONE = "Asia/Shanghai"
# TIME_ZONE = "UTC"
LANGUAGE_CODE = "zh-hans"
# LANGUAGE_CODE = "en-us"
LANGUAGES = (
    ("en", "English"),
    ("zh-hans", "简体中文"),
)

# open环境使用cookie中的blueking_language来控制语言
LANGUAGE_SESSION_KEY = "blueking_language"
LANGUAGE_COOKIE_NAME = os.getenv("BKAPP_LANGUAGE_COOKIE_NAME", "blueking_language")
IS_DISPLAY_LANGUAGE_CHANGE = "none"
