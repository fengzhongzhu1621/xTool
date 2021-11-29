# -*- coding: utf-8 -*-

import textwrap
import string
import logging
from functools import wraps
from collections import deque
import socket
import random
from datetime import timedelta

from typing import Callable, Optional, TypeVar, cast, Sequence, Union
from xTool.type_hint import Protocol
from xTool.exceptions import InvalidStatsNameException
from xTool.plugins.plugin import PluginType, register_plugin, get_plugin_instance
from xTool.utils.timer import Timer
from xTool.decorators.utils import safe_wraps
from xTool.utils.dates import time_now

log = logging.getLogger(__name__)

T = TypeVar("T", bound=Callable)  # pylint: disable=invalid-name
ALLOWED_CHARACTERS = set(string.ascii_letters + string.digits + "_.-")
STATS_NAME_DEFAULT_MAX_LENGTH = 250


class StatsClientBase(object):
    """A Base class for various statsd clients."""

    def __init__(self):
        # 指令前缀
        self._prefix = None

    def close(self):
        """Used to close and clean up any underlying resources."""
        raise NotImplementedError()

    def _send(self, *args, **kwargs):
        """发送指标，调用服务端接口 ."""
        raise NotImplementedError()

    def pipeline(self):
        """一次发送多个命令 ."""
        raise NotImplementedError()

    def timer(self, stat, rate=1):
        """创建一个计时器，计算一个操作的耗时，单位是ms ."""
        return StatsdTimer(self, stat, rate)

    def timing(self, stat, delta, rate=1):
        """
        Send new timing information.

        `delta` can be either a number of milliseconds or a timedelta.
        """
        if isinstance(delta, timedelta):
            # Convert timedelta to number of milliseconds.
            delta = delta.total_seconds() * 1000.0
        self._send_stat(stat, "%0.6f|ms" % delta, rate)

    def incr(self, stat, count=1, rate=1):
        """Increment a stat by `count`. 区间计数 ."""
        self._send_stat(stat, "%s|c" % count, rate)

    def decr(self, stat, count=1, rate=1):
        """Decrement a stat by `count`. 区间计数 ."""
        self.incr(stat, -count, rate)

    def gauge(self, stat, value, rate=1, delta=False):
        """Set a gauge value. 发送一个测量值，flush时不会清空，保持原有值 ."""
        if value < 0 and not delta:
            # 客户端采样，减少请求调用
            if rate < 1:
                if random.random() > rate:
                    return
            # 重置为负数
            with self.pipeline() as pipe:
                # 重置为初始值0
                pipe._send_stat(stat, "0|g", 1)
                # 初始化值为一个负数
                pipe._send_stat(stat, "%s|g" % value, 1)
        else:
            # 需要对前面的值进行加法操作
            prefix = "+" if delta and value >= 0 else ""
            self._send_stat(stat, "%s%s|g" % (prefix, value), rate)

    def set(self, stat, value, rate=1):
        """Set a set value. 记录flush期间，不重复的值 ."""
        self._send_stat(stat, "%s|s" % value, rate)

    def _send_stat(self, stat, value, rate):
        """发送指标 ."""
        self._after(self._prepare(stat, value, rate))

    def _prepare(self, stat, value, rate):
        """客户端采样 ."""
        if rate < 1:
            if random.random() > rate:
                return
            value = "%s|@%s" % (value, rate)
        # metrics名称添加前缀
        if self._prefix:
            stat = "%s.%s" % (self._prefix, stat)

        return "%s:%s" % (stat, value)

    def _after(self, data):
        if data:
            self._send(data)


class PipelineBase(StatsClientBase):
    def __init__(self, client):
        super().__init__()
        self._client = client
        # 命令前缀
        self._prefix = client._prefix
        # 缓存命令
        self._stats = deque()

    def _send(self):
        raise NotImplementedError()

    def _after(self, data):
        """发送命令时，先缓存到队列；上下文结束时再批量发给服务器 ."""
        if data is not None:
            # 队列尾部添加数据
            self._stats.append(data)

    def __enter__(self):
        return self

    def __exit__(self, typ, value, tb):
        self.send()

    def send(self):
        if not self._stats:
            return
        self._send()

    def pipeline(self):
        return self.__class__(self)


class StatsClient(StatsClientBase):
    """A client for statsd. （线程安全）"""

    def __init__(
        self, host="localhost", port=8125, prefix=None, maxudpsize=512, ipv6=False
    ):
        """Create a new client."""
        super().__init__()
        # 解析主机地址
        fam = socket.AF_INET6 if ipv6 else socket.AF_INET
        family, _, _, _, addr = socket.getaddrinfo(host, port, fam, socket.SOCK_DGRAM)[
            0
        ]
        self._addr = addr
        # 创建socket
        self._sock = socket.socket(family, socket.SOCK_DGRAM)
        self._sock.setblocking(False)
        self._prefix = prefix
        # 仅用于管道缓冲
        self._maxudpsize = maxudpsize

    def _send(self, data):
        """Send data to statsd."""
        try:
            self._sock.sendto(data.encode("ascii"), self._addr)
        except (socket.error, RuntimeError):
            # No time for love, Dr. Jones!
            pass

    def close(self):
        if self._sock and hasattr(self._sock, "close"):
            self._sock.close()
        self._sock = None

    def pipeline(self):
        """创建管道client ."""
        return Pipeline(self)


class Pipeline(PipelineBase):
    """命令管道(线程不安全) ."""

    def __init__(self, client):
        super().__init__(client)
        # 客户端缓冲区的大小
        self._maxudpsize = client._maxudpsize

    def _send(self):
        # 从队列中获取数据
        data = self._stats.popleft()
        while self._stats:
            # Use popleft to preserve the order of the stats.
            stat = self._stats.popleft()
            if len(stat) + len(data) + 1 >= self._maxudpsize:
                # 缓冲区满发送，向服务器发送剩余数据
                self._client._after(data)
                data = stat
            else:
                # 多条命令换行分割
                data = "{}\n{}".format(data, stat)
        # 队列为空时向服务器发送剩余数据
        self._client._after(data)


class StreamPipeline(PipelineBase):
    def _send(self):
        self._client._after("\n".join(self._stats))
        # 清空队列
        self._stats.clear()


class StreamClientBase(StatsClientBase):
    def __init__(self):
        super().__init__()
        self._sock = None

    def connect(self):
        raise NotImplementedError()

    def close(self):
        if self._sock and hasattr(self._sock, "close"):
            self._sock.close()
        self._sock = None

    def reconnect(self):
        self.close()
        self.connect()

    def pipeline(self):
        return StreamPipeline(self)

    def _send(self, data):
        """Send data to statsd."""
        if not self._sock:
            self.connect()
        self._do_send(data)

    def _do_send(self, data):
        self._sock.sendall(data.encode("ascii") + b"\n")


class TCPStatsClient(StreamClientBase):
    """TCP version of StatsClient."""

    def __init__(
        self, host="localhost", port=8125, prefix=None, timeout=None, ipv6=False
    ):
        """Create a new client."""
        super().__init__()
        self._host = host
        self._port = port
        self._ipv6 = ipv6
        self._timeout = timeout
        self._prefix = prefix
        self._sock = None

    def connect(self):
        fam = socket.AF_INET6 if self._ipv6 else socket.AF_INET
        family, _, _, _, addr = socket.getaddrinfo(
            self._host, self._port, fam, socket.SOCK_STREAM
        )[0]
        self._sock = socket.socket(family, socket.SOCK_STREAM)
        self._sock.settimeout(self._timeout)
        self._sock.connect(addr)


class UnixSocketStatsClient(StreamClientBase):
    """Unix domain socket version of StatsClient."""

    def __init__(self, socket_path, prefix=None, timeout=None):
        """Create a new client."""
        super().__init__()
        self._socket_path = socket_path
        self._timeout = timeout
        self._prefix = prefix
        self._sock = None

    def connect(self):
        self._sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self._sock.settimeout(self._timeout)
        self._sock.connect(self._socket_path)


class StatsdTimer(object):
    """A context manager/decorator for statsd.timing()."""

    def __init__(self, client, stat, rate=1):
        self.client = client  # statd客户端
        self.stat = stat  # 指标
        self.rate = rate  # 采样
        self.ms = None  # 耗时
        self._sent = False  # 是否已经发送
        self._start_time = None

    def __call__(self, f):
        """Thread-safe timing function decorator."""

        @safe_wraps(f)
        def _wrapped(*args, **kwargs):
            start_time = time_now()
            try:
                return f(*args, **kwargs)
            finally:
                elapsed_time_ms = 1000.0 * (time_now() - start_time)
                self.client.timing(self.stat, elapsed_time_ms, self.rate)

        return _wrapped

    def __enter__(self):
        return self.start()

    def __exit__(self, typ, value, tb):
        self.stop()

    def start(self):
        """开始计时 ."""
        self.ms = None
        self._sent = False
        self._start_time = time_now()
        return self

    def stop(self, send=True):
        """结束计时，并发送指标 ."""
        if self._start_time is None:
            raise RuntimeError("Timer has not started.")
        # 计算耗时（ms）
        dt = time_now() - self._start_time
        self.ms = 1000.0 * dt  # Convert to milliseconds.
        # 发送指标
        if send:
            self.send()
        return self

    def send(self):
        if self.ms is None:
            raise RuntimeError("No data recorded.")
        if self._sent:
            raise RuntimeError("Already sent data.")
        # 标记指标已经发送
        self._sent = True
        # 发送指标
        self.client.timing(self.stat, self.ms, self.rate)


class TimerProtocol(Protocol):
    """Type protocol for StatsLogger.timer"""

    def __enter__(self):
        ...

    def __exit__(self, exc_type, exc_value, traceback):
        ...

    def start(self):
        """Start the timer"""
        ...

    def stop(self, send=True):
        """Stop, and (by default) submit the timer to statsd"""
        ...


class StatsLogger(Protocol):
    """This class is only used for TypeChecking (for IDEs, mypy, pylint, etc)"""

    @classmethod
    def incr(cls, stat: str, count: int = 1, rate: int = 1) -> None:
        """Increment stat"""

    @classmethod
    def decr(cls, stat: str, count: int = 1, rate: int = 1) -> None:
        """Decrement stat"""

    @classmethod
    def gauge(cls, stat: str, value: float, rate: int = 1, delta: bool = False) -> None:
        """Gauge stat"""

    @classmethod
    def timing(cls, stat: str, dt) -> None:
        """Stats timing"""

    @classmethod
    def timer(cls, *args, **kwargs) -> TimerProtocol:
        """Timer metric that can be cancelled"""


class StatsNameConfig:
    def __init__(self, name="default", max_length=STATS_NAME_DEFAULT_MAX_LENGTH):
        self.name = name
        self.max_length = max_length


class StatsAllowNameValidatorConfig:
    def __init__(self, name, allow_list=None):
        self.name = name
        self.allow_list = allow_list if allow_list else []


@register_plugin(plugin_type=PluginType.STATS_NAME_HANDLER, plugin_name="default")
class DefaultStatNameHandler:
    def handler(self, stat_name, max_length) -> str:
        """A function that validate the statsd stat name, apply changes to the stat name
        if necessary and return the transformed stat name.
        """
        if not isinstance(stat_name, str):
            raise InvalidStatsNameException("The stat_name has to be a string")
        if len(stat_name) > max_length:
            raise InvalidStatsNameException(
                textwrap.dedent(
                    """\
                The stat_name ({stat_name}) has to be less than {max_length} characters.
            """.format(
                        stat_name=stat_name, max_length=max_length
                    )
                )
            )
        if not all((c in ALLOWED_CHARACTERS) for c in stat_name):
            raise InvalidStatsNameException(
                textwrap.dedent(
                    """\
                The stat name ({stat_name}) has to be composed with characters in
                {allowed_characters}.
                """.format(
                        stat_name=stat_name, allowed_characters=ALLOWED_CHARACTERS
                    )
                )
            )
        return stat_name


def get_current_handler_stat_name_func(name: Optional[str] = None):
    """Get Stat Name Handler from pluginStore"""
    name = name if name else "default"
    return get_plugin_instance(PluginType.STATS_NAME_HANDLER, name)


def validate_stat(fn: T) -> T:
    """Check if stat name contains invalid characters.
    Log and not emit stats if name is invalid
    """

    @wraps(fn)
    def wrapper(_self, stat=None, *args, **kwargs):
        try:
            if stat is not None:
                if _self.stats_name_config:
                    name = _self.stats_name_config.name
                    max_length = _self.stats_name_config.max_length
                else:
                    name = "default"
                    max_length = STATS_NAME_DEFAULT_MAX_LENGTH
                handler_stat_name_func = get_current_handler_stat_name_func(
                    name
                ).handler
                stat = handler_stat_name_func(stat, max_length)
            return fn(_self, stat, *args, **kwargs)
        except InvalidStatsNameException:
            log.error("Invalid stat name: %s.", stat, exc_info=True)
            return None

    return cast(T, wrapper)


class AllowListValidatorProtocol(Protocol):
    def set_allow_list(self, allow_list: Optional[Union[Sequence[str], str]]) -> None:
        ...

    def test(self, stat: str) -> bool:
        ...


@register_plugin(
    plugin_type=PluginType.STATS_NAME_ALLOW_VALIDATOR, plugin_name="default"
)
class DefaultAllowListValidator:
    """Class to filter unwanted stats"""

    def __init__(self, allow_list=None):
        self.allow_list = None
        self.set_allow_list(allow_list)

    def set_allow_list(self, allow_list: Optional[Union[Sequence[str], str]]) -> None:
        if allow_list:
            # pylint: disable=consider-using-generator
            if isinstance(allow_list, str):
                self.allow_list = tuple(
                    [item.strip().lower() for item in allow_list.split(",")]
                )
        else:
            self.allow_list = None

    def test(self, stat: str) -> bool:
        """Test if stat is in the Allow List"""
        if self.allow_list is not None:
            return stat.strip().lower().startswith(self.allow_list)
        else:
            return True  # default is all metrics allowed


def get_current_allow_list_validator(
    name: Optional[str] = None,
) -> AllowListValidatorProtocol:
    name = name if name else "default"
    return get_plugin_instance(PluginType.STATS_NAME_ALLOW_VALIDATOR, name)


class StatsParamConfig:
    def __init__(
        self,
        statsd_host="localhost",
        statsd_port=8125,
        statsd_prefix=None,
        constant_tags=None,
    ):
        self.statsd_host = statsd_host
        self.statsd_port = statsd_port
        self.statsd_prefix = statsd_prefix
        if constant_tags is None or constant_tags == "":
            self.constant_tags = []
        else:
            self.constant_tags = [key_value for key_value in constant_tags.split(",")]


class BaseStatsdLogger:
    def __init__(
        self,
        statsd_client=None,
        stats_name_config: Optional[StatsNameConfig] = None,
        allow_name_validator_config: Optional[StatsAllowNameValidatorConfig] = None,
    ):
        self.statsd = statsd_client
        self.stats_name_config = None
        self.allow_name_validator_config = None
        self.allow_list_validator = None
        self.set_validator(stats_name_config, allow_name_validator_config)

    def create_client(self, statsd_config: StatsParamConfig):
        raise NotImplementedError

    def set_validator(self, stats_name_config, allow_name_validator_config):
        self.stats_name_config = stats_name_config
        self.allow_name_validator_config = allow_name_validator_config
        if self.allow_name_validator_config:
            allow_validator_name = self.allow_name_validator_config.name
            allow_list = self.allow_name_validator_config.allow_list
        else:
            allow_validator_name = None
            allow_list = None
        self.allow_list_validator = get_current_allow_list_validator(
            allow_validator_name
        )
        self.allow_list_validator.set_allow_list(allow_list)


@register_plugin(plugin_type=PluginType.STATS_LOGGER, plugin_name="default")
class DummyStatsLogger:
    """If no StatsLogger is configured, DummyStatsLogger is used as a fallback"""

    @classmethod
    def incr(cls, stat, count=1, rate=1):
        """Increment stat"""

    @classmethod
    def decr(cls, stat, count=1, rate=1):
        """Decrement stat"""

    @classmethod
    def gauge(cls, stat, value, rate=1, delta=False):
        """Gauge stat"""

    @classmethod
    def timing(cls, stat, dt):
        """Stats timing"""

    @classmethod
    def timer(cls, *args, **kwargs):  # pylint: disable=unused-argument
        """Timer metric that can be cancelled"""
        return Timer()

    @classmethod
    def set(cls, stat, dt):
        """Stats set"""


@register_plugin(plugin_type=PluginType.STATS_LOGGER, plugin_name="statsd")
class SafeStatsdLogger(BaseStatsdLogger):
    """Statsd Logger"""

    def __init__(
        self,
        statsd_client=None,
        stats_name_config: Optional[StatsNameConfig] = None,
        allow_name_validator_config: Optional[StatsAllowNameValidatorConfig] = None,
    ):
        super().__init__(statsd_client, stats_name_config, allow_name_validator_config)

    def create_client(self, statsd_config: StatsParamConfig):
        from statsd import StatsClient

        statsd = StatsClient(
            host=statsd_config.statsd_host,
            port=statsd_config.statsd_port,
            prefix=statsd_config.statsd_prefix,
        )
        self.statsd = statsd

    @validate_stat
    def incr(self, stat, count=1, rate=1):
        """Increment stat

        最简单的metric应该就是counter，也就是通常的计数功能，StatsD会将收到的counter value累加，然后在flush的时候输出，并且重新清零。
        所以我们用counter就能非常方便的查看一段时间某个操作的频率，
        譬如对于一个HTTP服务来说，我们可以使用counter来统计request的次数，finish这个request的次数以及fail的次数。
        """
        if self.allow_list_validator.test(stat):
            return self.statsd.incr(stat, count, rate)
        return None

    @validate_stat
    def decr(self, stat, count=1, rate=1):
        """Decrement stat"""
        if self.allow_list_validator.test(stat):
            return self.statsd.decr(stat, count, rate)
        return None

    @validate_stat
    def gauge(self, stat, value, rate=1, delta=False):
        """Gauge stat"""
        if self.allow_list_validator.test(stat):
            return self.statsd.gauge(stat, value, rate, delta)
        return None

    @validate_stat
    def timing(self, stat, dt):
        """Stats timing

        记录某个操作的耗时
        """
        if self.allow_list_validator.test(stat):
            return self.statsd.timing(stat, dt)
        return None

    @validate_stat
    def timer(self, stat=None, *args, **kwargs):
        """Timer metric that can be cancelled"""
        if stat and self.allow_list_validator.test(stat):
            return Timer(self.statsd.timer(stat, *args, **kwargs))
        return Timer()

    @validate_stat
    def set(self, stat, dt):
        if self.allow_list_validator.test(stat):
            return self.statsd.set(stat, dt)
        return None


@register_plugin(plugin_type=PluginType.STATS_LOGGER, plugin_name="dog_statsd")
class SafeDogStatsdLogger(BaseStatsdLogger):
    """DogStatsd Logger"""

    def __init__(
        self,
        dog_statsd_client=None,
        stats_name_config: Optional[StatsNameConfig] = None,
        allow_name_validator_config: Optional[StatsAllowNameValidatorConfig] = None,
    ):
        super().__init__(
            dog_statsd_client, stats_name_config, allow_name_validator_config
        )

    def create_client(self, statsd_config: StatsParamConfig):
        from datadog import DogStatsd  # noqa

        statsd = DogStatsd(
            host=statsd_config.statsd_host,
            port=statsd_config.statsd_port,
            namespace=statsd_config.statsd_prefix,
            constant_tags=statsd_config.statsd_prefix,
        )
        self.statsd = statsd

    @validate_stat
    def incr(self, stat, count=1, rate=1, tags=None):
        """Increment stat"""
        if self.allow_list_validator.test(stat):
            tags = tags or []
            return self.statsd_client.increment(
                metric=stat, value=count, tags=tags, sample_rate=rate
            )
        return None

    @validate_stat
    def decr(self, stat, count=1, rate=1, tags=None):
        """Decrement stat"""
        if self.allow_list_validator.test(stat):
            tags = tags or []
            return self.statsd_client.decrement(
                metric=stat, value=count, tags=tags, sample_rate=rate
            )
        return None

    @validate_stat
    def gauge(
        self, stat, value, rate=1, delta=False, tags=None
    ):  # pylint: disable=unused-argument
        """Gauge stat"""
        if self.allow_list_validator.test(stat):
            tags = tags or []
            return self.statsd_client.gauge(
                metric=stat, value=value, tags=tags, sample_rate=rate
            )
        return None

    @validate_stat
    def timing(self, stat, dt, tags=None):
        """Stats timing"""
        if self.allow_list_validator.test(stat):
            tags = tags or []
            return self.statsd_client.timing(metric=stat, value=dt, tags=tags)
        return None

    @validate_stat
    def timer(self, stat=None, *args, tags=None, **kwargs):
        """Timer metric that can be cancelled"""
        if stat and self.allow_list_validator.test(stat):
            tags = tags or []
            return Timer(self.statsd_client.timed(stat, *args, tags=tags, **kwargs))
        return Timer()

    @classmethod
    def set(cls, stat, dt):
        """Stats set"""


def get_stats_logger(name: Optional[str] = None) -> StatsLogger:
    """获得默认的statsd client ."""
    name = name if name else "default"
    return get_plugin_instance(PluginType.STATS_LOGGER, name)
