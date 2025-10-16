from django.apps import AppConfig


class QuickstartConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    # 指向此应用程序的完整的 Python 格式的路径
    # 每个 AppConfig 子类都必须包含此项。
    # 它必须在整个 Django 项目中唯一。
    name = 'apps.quickstart'
