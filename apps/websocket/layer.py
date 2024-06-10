from django.core.signals import setting_changed


class ChannelLayerManager:
    """
    Takes a settings dictionary of backends and initialises them on request.
    """

    def __init__(self):
        self.backends = {}
        setting_changed.connect(self._reset_backends)

    def _reset_backends(self, setting, **kwargs):
        """
        Removes cached channel layers when the CHANNEL_LAYERS setting changes.
        """
        if setting == "CHANNEL_LAYERS":
            self.backends = {}
