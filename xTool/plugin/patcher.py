"""
补丁基类

https://github.com/uber-common/opentracing-python-instrumentation/blob/master/opentracing_instrumentation/client_hooks/mysqldb.py
https://github.com/uber-common/opentracing-python-instrumentation/blob/master/opentracing_instrumentation/client_hooks/__init__.py
"""


class Patcher:

    def __init__(self):
        self.patches_installed = False

    @property
    def applicable(self):
        """是否满足安装条件 ."""
        raise NotImplementedError

    def install_patches(self):
        if self.patches_installed:
            return

        if self.applicable:
            self._install_patches()
        self.patches_installed = True

    def reset_patches(self):
        if self.applicable:
            self._reset_patches()
        self.patches_installed = False

    def _install_patches(self):
        raise NotImplementedError

    def _reset_patches(self):
        raise NotImplementedError

    @classmethod
    def configure_hook_module(cls, context):
        def set_patcher(custom_patcher):
            context["patcher"] = custom_patcher

        def install_patches():
            context["patcher"].install_patches()

        def reset_patches():
            context["patcher"].reset_patches()

        context["patcher"] = cls()
        context["set_patcher"] = set_patcher
        context["install_patches"] = install_patches
        context["reset_patches"] = reset_patches
