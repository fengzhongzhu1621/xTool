import os

from config import BASE_DIR

# TEMPLATES 是 Django 项目中的一个关键配置项，用于定义模板引擎及其相关设置。
# Django 支持多种模板引擎，但最常用的是内置的 DjangoTemplates 引擎。
# 通过 TEMPLATES 配置，您可以指定模板的位置、加载方式以及上下文处理器等。

# "django.template.backends.django.DjangoTemplates" 是 Django 内置的模板引擎，用于处理 .html 等模板文件。

TEMPLATE_CONTEXT_PROCESSORS = [
    # 向模板上下文添加 debug 和 sql_queries 变量。
    # 在开发环境中，debug 变量可以帮助判断当前是否处于调试模式；sql_queries 可以用于查看执行的 SQL 查询（需要额外配置）。
    "django.template.context_processors.debug",
    # 向模板上下文添加 request 变量，包含当前请求的所有信息。
    # 在模板中访问请求对象，例如获取当前 URL、用户代理等。
    # 需要确保 django.template.context_processors.request 已启用，
    # 并且在 MIDDLEWARE 中包含 django.middleware.common.CommonMiddleware 或其他适当的中间件。
    "django.template.context_processors.request",
    # 向模板上下文添加与认证相关的变量，如 user 和 perms。
    # 在模板中访问当前登录用户的信息，以及权限检查。
    "django.contrib.auth.context_processors.auth",
    # 向模板上下文添加 messages 变量，包含所有消息框架的消息。
    # 在模板中显示用户通知、警告或其他类型的消息。
    "django.contrib.messages.context_processors.messages",
]
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        # 项目级模板目录
        "DIRS": [os.path.join(BASE_DIR, "static"), os.path.join(BASE_DIR, "staticfiles")],
        # Django 首先会在 DIRS 中指定的目录中查找模板，如果未找到，则会在各个应用的 templates 目录中查找。
        # 在每个已安装应用的 templates 目录中查找模板文件。允许每个应用拥有自己的模板，并且 Django 会按照 INSTALLED_APPS 的顺序搜索这些模板。
        "APP_DIRS": True,
        "OPTIONS": {
            # 当模板中引用了一个未定义的变量时，Django 会使用 string_if_invalid 指定的字符串替换该变量。
            # 这里的值是 "{{%s}}"，意味着未定义的变量会被替换为 {{变量名}}。
            "string_if_invalid": "{{%s}}",
            "context_processors": TEMPLATE_CONTEXT_PROCESSORS,
        },
    },
]
