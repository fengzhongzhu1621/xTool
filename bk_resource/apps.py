from django.apps import AppConfig

from bk_resource.management.root import setup


class BKResourceConfig(AppConfig):
    name = "bk_resource"
    verbose_name = "bk_resource"
    label = "bk_resource"

    def ready(self):
        setup()
