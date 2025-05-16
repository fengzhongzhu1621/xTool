import os

from config import BASE_DIR

IS_LOCAL = not os.getenv("ENVIRONMENT", False)
if not IS_LOCAL:
    STATIC_ROOT = "staticfiles"
else:
    STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")


# 静态资源文件(js,css等）在APP上线更新后, 由于浏览器有缓存,
# 可能会造成没更新的情况. 所以在引用静态资源的地方，都把这个加上
# Django 模板中：<script src="/a.js?v=${STATIC_VERSION}"></script>
# 如果静态资源修改了以后，上线前改这个版本号即可
STATIC_VERSION = "1.0"

STATICFILES_DIRS = [os.path.join(BASE_DIR, "static")]  # noqa

# The default file storage backend used during the build process
STATICFILES_STORAGE = "django.contrib.staticfiles.storage.StaticFilesStorage"
