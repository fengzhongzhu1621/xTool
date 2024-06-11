from typing import Dict


class ProtocolTypeRouter:
    """
    Takes a mapping of protocol type names to other Application instances,
    and dispatches to the right one based on protocol name (or raises an error)
    """

    def __init__(self, application_mapping: Dict) -> None:
        self.application_mapping = application_mapping

    async def __call__(self, scope, receive, send):
        if scope["type"] in self.application_mapping:
            application = self.application_mapping[scope["type"]]
            return await application(scope, receive, send)
        else:
            raise ValueError("No application configured for scope type %r" % scope["type"])


class ChannelNameRouter:
    """
    Maps to different applications based on a "channel" key in the scope
    (intended for the Channels worker mode)
    """

    def __init__(self, application_mapping: Dict) -> None:
        self.application_mapping = application_mapping

    async def __call__(self, scope, receive, send):
        if "channel" not in scope:
            raise ValueError(
                "ChannelNameRouter got a scope without a 'channel' key. "
                + "Did you make sure it's only being used for 'channel' type messages?"
            )
        if scope["channel"] in self.application_mapping:
            application = self.application_mapping[scope["channel"]]
            return await application(scope, receive, send)
        else:
            raise ValueError("No application configured for channel name %r" % scope["channel"])
