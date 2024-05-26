from bk_resource.management.root import setup
from django.apps import AppConfig


class BKResourceConfig(AppConfig):
    name = "bk_resource"
    verbose_name = "bk_resource"
    label = "bk_resource"

    def ready(self):
        setup()
