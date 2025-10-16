from typing import Dict

from django.conf import settings
from django.core.signals import setting_changed
from django.utils.module_loading import import_string

from .exceptions import InvalidBackendError


class BackendInstanceManager:
    """
    Takes a settings dictionary of backends and initialises them on request.
    """

    def __init__(self, setting_name: str) -> None:
        self.backends = {}
        self.setting_name = setting_name
        # settings.CHANNEL_LAYERS 值发生变化时，重置 self.backends 的值为 {}
        setting_changed.connect(self._reset_backends)

    def _reset_backends(self, setting, **kwargs) -> None:
        """
        Removes cached channel layers when the CHANNEL_LAYERS setting changes.
        """
        if setting == self.setting_name:
            self.backends = {}

    @property
    def configs(self) -> Dict:
        # Lazy load settings so we can be imported
        return getattr(settings, self.setting_name, {})

    def make_backend(self, key: str):
        """
        Instantiate channel layer.
        """
        # 获取构造实例需要的构造函数参数
        config = self.configs[key].get("CONFIG", {})
        # 根据配置动态创建实例
        return self._make_backend(key, config)

    def make_test_backend(self, key: str):
        """
        Instantiate channel layer using its test config.
        """
        try:
            config = self.configs[key]["TEST_CONFIG"]
        except KeyError:
            raise InvalidBackendError("No TEST_CONFIG specified for %s" % key)
        return self._make_backend(key, config)

    def _make_backend(self, key: str, config: Dict):
        """根据配置动态创建 ChannelLayer 实例"""
        # Check for old format config
        if "ROUTING" in self.configs[key]:
            raise InvalidBackendError("ROUTING key found for %s - this is no longer needed in Channels 2." % key)
        # Load the backend class
        try:
            backend_class = import_string(self.configs[key]["BACKEND"])
        except KeyError:
            raise InvalidBackendError("No BACKEND specified for %s" % key)
        except ImportError:
            raise InvalidBackendError(
                "Cannot import BACKEND {!r} specified for {}".format(self.configs[key]["BACKEND"], key)
            )
        # Initialise and pass config
        return backend_class(**config)

    def __getitem__(self, key: str):
        if key not in self.backends:
            self.backends[key] = self.make_backend(key)
        return self.backends[key]

    def __contains__(self, key: str) -> bool:
        return key in self.configs

    def set(self, key, layer):
        old = self.backends.get(key, None)
        self.backends[key] = layer
        return old
