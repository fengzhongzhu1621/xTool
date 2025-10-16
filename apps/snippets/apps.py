from django.apps import AppConfig


class SnippetsAppConfig(AppConfig):
    name = 'apps.snippets'

    def ready(self):
        # import_module("xTool.apps.snippets.resources")
        pass
