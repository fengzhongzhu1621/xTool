from typing import TYPE_CHECKING

from .type_hint import _Plugin

if TYPE_CHECKING:
    pass


class PluginValidationError(Exception):
    """Plugin failed validation.

    :param plugin: The plugin which failed validation.
    :param message: Error message.
    """

    def __init__(self, plugin: _Plugin, message: str) -> None:
        super().__init__(message)
        #: The plugin which failed validation.
        self.plugin = plugin


class HookCallError(Exception):
    """Hook was called incorrectly."""
