import asyncio
import fnmatch
import random
import re
import string
import time
from copy import deepcopy
from typing import Dict, List, Optional

from apps.websocket import DEFAULT_CHANNEL_LAYER
from core.settings.backend import BackendInstanceManager

from .exceptions import ChannelFull


class ChannelLayerManager(BackendInstanceManager):
    """
    Takes a settings dictionary of backends and initialises them on request.

    用于管理多个 ChannelLayer 实例。允许你在应用程序中使用多个通道层，以便在不同的上下文（如不同的服务或组件）之间进行通信。
    ChannelLayer 是一个抽象类，用于处理跨进程通信，例如在分布式系统中发送和接收消息。

    1. 管理多个通道层：ChannelLayerManager 允许你同时使用多个 ChannelLayer 实例。这对于在分布式系统中实现跨服务通信非常有用。
    2. 简化通道层的使用：通过使用 ChannelLayerManager，你可以更容易地在应用程序中使用多个通道层，而无需手动管理每个通道层的实例。
    3. 提供统一的 API：ChannelLayerManager 为所有管理的通道层提供了统一的 API，使得在不同通道层之间切换变得容易。
    """

    def __init__(self) -> None:
        super().__init__("CHANNEL_LAYERS")


class BaseChannelLayer:
    """
    Base channel layer class that others can inherit from, with useful
    common functionality.
    """

    # 名字的最大长度
    MAX_NAME_LENGTH = 100

    def __init__(self, expiry: int = 60, capacity: int = 100, channel_capacity: Optional[Dict] = None):
        # 通道中每个消息的存活时间
        self.expiry = expiry
        # 通道的最大容量
        self.capacity = capacity
        self.channel_capacity = channel_capacity or {}

    def compile_capacities(self, channel_capacity: Dict) -> List:
        """
        格式化 channel_capacity 的值，将通配符模式转换为正则表达式。

        Takes an input channel_capacity dict and returns the compiled list
        of regexes that get_capacity will look for as self.channel_capacity
        """
        result = []
        for pattern, value in channel_capacity.items():
            # If they passed in a precompiled regex, leave it, else interpret
            # it as a glob.
            if hasattr(pattern, "match"):
                result.append((pattern, value))
            else:
                # 将 shell-style 通配符模式转换为正则表达式。
                result.append((re.compile(fnmatch.translate(pattern)), value))
        return result

    def get_capacity(self, channel):
        """
        获得第一个匹配的通道的容量

        Gets the correct capacity for the given channel; either the default,
        or a matching result from channel_capacity. Returns the first matching
        result; if you want to control the order of matches, use an ordered dict
        as input.
        """
        for pattern, capacity in self.channel_capacity:
            if pattern.match(channel):
                return capacity
        return self.capacity

    def match_type_and_length(self, name):
        if isinstance(name, str) and (len(name) < self.MAX_NAME_LENGTH):
            return True
        return False

    # Name validation functions

    channel_name_regex = re.compile(r"^[a-zA-Z\d\-_.]+(\![\d\w\-_.]*)?$")
    group_name_regex = re.compile(r"^[a-zA-Z\d\-_.]+$")
    invalid_name_error = (
        "{} name must be a valid unicode string "
        + "with length < {} ".format(MAX_NAME_LENGTH)
        + "containing only ASCII alphanumerics, hyphens, underscores, or periods, "
        + "not {}"
    )

    def valid_channel_name(self, name, receive=False):
        if self.match_type_and_length(name):
            if bool(self.channel_name_regex.match(name)):
                # Check cases for special channels
                if "!" in name and not name.endswith("!") and receive:
                    raise TypeError("Specific channel names in receive() must end at the !")
                return True
        raise TypeError(self.invalid_name_error.format("Channel", name))

    def valid_group_name(self, name):
        if self.match_type_and_length(name):
            if bool(self.group_name_regex.match(name)):
                return True
        raise TypeError(self.invalid_name_error.format("Group", name))

    def valid_channel_names(self, names, receive=False):
        _non_empty_list = True if names else False
        _names_type = isinstance(names, list)
        assert _non_empty_list and _names_type, "names must be a non-empty list"

        assert all(self.valid_channel_name(channel, receive=receive) for channel in names)
        return True

    def non_local_name(self, name):
        """
        Given a channel name, returns the "non-local" part. If the channel name
        is a process-specific channel (contains !) this means the part up to
        and including the !; if it is anything else, this means the full name.
        """
        if "!" in name:
            return name[: name.find("!") + 1]
        else:
            return name


class InMemoryChannelLayer(BaseChannelLayer):
    """
    In-memory channel layer implementation
    """

    def __init__(self, expiry=60, group_expiry=86400, capacity=100, channel_capacity=None, **kwargs):
        super().__init__(expiry=expiry, capacity=capacity, channel_capacity=channel_capacity, **kwargs)
        self.channels = {}
        self.groups = {}
        self.group_expiry = group_expiry

    # Channel layer API

    extensions = ["groups", "flush"]

    async def send(self, channel_name: str, message: Dict):
        """
        Send a message onto a (general or specific) channel.
        """
        # Typecheck
        assert isinstance(message, dict), "message is not a dict"
        assert self.valid_channel_name(channel_name), "Channel name not valid"
        # If it's a process-local channel, strip off local part and stick full
        # name in message
        assert "__asgi_channel__" not in message

        # 每个通道创建一个异步队列
        queue = self.channels.setdefault(channel_name, asyncio.Queue())
        # 队列已满抛出异常
        if queue.qsize() >= self.capacity:
            raise ChannelFull(channel_name)

        # 将消息发送到队列，并设置过期时间
        await queue.put((time.time() + self.expiry, deepcopy(message)))

    async def receive(self, channel_name):
        """
        Receive the first message that arrives on the channel.
        If more than one coroutine waits on the same channel, a random one
        of the waiting coroutines will get the result.
        """
        assert self.valid_channel_name(channel_name)
        self._clean_expired()

        queue = self.channels.setdefault(channel_name, asyncio.Queue())

        # Do a plain direct receive
        try:
            _, message = await queue.get()
        finally:
            # 队列为空则注销此通道
            if queue.empty():
                del self.channels[channel_name]

        return message

    async def new_channel(self, prefix="specific."):
        """
        Returns a new channel name that can be used by something in our
        process as a specific channel.
        """
        return "{}.inmemory!{}".format(
            prefix,
            "".join(random.choice(string.ascii_letters) for i in range(12)),
        )

    # Expire cleanup

    def _clean_expired(self):
        """
        Goes through all messages and groups and removes those that are expired.
        Any channel with an expired message is removed from all groups.
        """
        # Channel cleanup
        for channel_name, queue in list(self.channels.items()):
            # 队列非空，且存在过期数据
            while not queue.empty() and queue._queue[0][0] < time.time():
                # 立即从队列中获取一个过期元素，而不等待元素可用
                queue.get_nowait()
                # Any removal prompts group discard
                self._remove_from_groups(channel_name)
                # Is the channel now empty and needs deleting?
                if queue.empty():
                    del self.channels[channel_name]

        # Group Expiration
        timeout = int(time.time()) - self.group_expiry
        for group in self.groups:
            for channel_name in list(self.groups.get(group, set())):
                # If join time is older than group_expiry end the group membership
                if self.groups[group][channel_name] and int(self.groups[group][channel_name]) < timeout:
                    # Delete from group
                    del self.groups[group][channel_name]

    # Flush extension

    async def flush(self):
        self.channels = {}
        self.groups = {}

    async def close(self):
        # Nothing to go
        pass

    def _remove_from_groups(self, channel_name):
        """
        Removes a channel from all groups. Used when a message on it expires.
        """
        for channels in self.groups.values():
            if channel_name in channels:
                del channels[channel_name]

    # Groups extension

    async def group_add(self, group_name: str, channel_name: str) -> None:
        """
        Adds the channel name to a group.
        """
        # Check the inputs
        assert self.valid_group_name(group_name), "Group name not valid"
        assert self.valid_channel_name(channel_name), "Channel name not valid"
        # Add to group dict
        self.groups.setdefault(group_name, {})
        self.groups[group_name][channel_name] = time.time()

    async def group_discard(self, group_name, channel_name):
        # Both should be text and valid
        assert self.valid_channel_name(channel_name), "Invalid channel name"
        assert self.valid_group_name(group_name), "Invalid group name"
        # Remove from group set
        if group_name in self.groups:
            if channel_name in self.groups[group_name]:
                del self.groups[group_name][channel_name]
            if not self.groups[group_name]:
                del self.groups[group_name]

    async def group_send(self, group, message):
        # Check types
        assert isinstance(message, dict), "Message is not a dict"
        assert self.valid_group_name(group), "Invalid group name"
        # Run clean
        self._clean_expired()
        # Send to each channel
        for channel in self.groups.get(group, set()):
            try:
                await self.send(channel, message)
            except ChannelFull:
                pass


def get_channel_layer(alias=DEFAULT_CHANNEL_LAYER):
    """
    Returns a channel layer by alias, or None if it is not configured.
    """
    try:
        return channel_layers[alias]
    except KeyError:
        return None


# Default global instance of the channel layer manager
channel_layers = ChannelLayerManager()
