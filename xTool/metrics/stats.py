# -*- coding: utf-8 -*-

import textwrap
import string
import logging
from functools import wraps

from typing import Callable, Optional, TypeVar, cast, Sequence, Union
from xTool.type_hint import Protocol
from xTool.exceptions import InvalidStatsNameException
from xTool.plugins.plugin import PluginType, register_plugin, get_plugin_instance
from xTool.utils.timer import Timer
from xTool.decorators.utils import safe_wraps
from xTool.utils.dates import time_now


log = logging.getLogger(__name__)

T = TypeVar("T", bound=Callable)  # pylint: disable=invalid-name
ALLOWED_CHARACTERS = set(string.ascii_letters + string.digits + '_.-')
STATS_NAME_DEFAULT_MAX_LENGTH = 250


class StatsdTimer(object):
    """A context manager/decorator for statsd.timing()."""

    def __init__(self, client, stat, rate=1):
        self.client = client
        self.stat = stat
        self.rate = rate
        self.ms = None
        self._sent = False
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
        self.ms = None
        self._sent = False
        self._start_time = time_now()
        return self

    def stop(self, send=True):
        if self._start_time is None:
            raise RuntimeError('Timer has not started.')
        dt = time_now() - self._start_time
        self.ms = 1000.0 * dt  # Convert to milliseconds.
        if send:
            self.send()
        return self

    def send(self):
        if self.ms is None:
            raise RuntimeError('No data recorded.')
        if self._sent:
            raise RuntimeError('Already sent data.')
        self._sent = True
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
    def gauge(
            cls,
            stat: str,
            value: float,
            rate: int = 1,
            delta: bool = False) -> None:
        """Gauge stat"""

    @classmethod
    def timing(cls, stat: str, dt) -> None:
        """Stats timing"""

    @classmethod
    def timer(cls, *args, **kwargs) -> TimerProtocol:
        """Timer metric that can be cancelled"""


class StatsNameConfig:
    def __init__(
            self,
            name="default",
            max_length=STATS_NAME_DEFAULT_MAX_LENGTH):
        self.name = name
        self.max_length = max_length


class StatsAllowNameValidatorConfig:
    def __init__(self, name, allow_list=None):
        self.name = name
        self.allow_list = allow_list if allow_list else []


@register_plugin(plugin_type=PluginType.STATS_NAME_HANDLER,
                 plugin_name="default")
class DefaultStatNameHandler:
    def handler(self, stat_name, max_length) -> str:
        """A function that validate the statsd stat name, apply changes to the stat name
        if necessary and return the transformed stat name.
        """
        if not isinstance(stat_name, str):
            raise InvalidStatsNameException('The stat_name has to be a string')
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
                        stat_name=stat_name,
                        allowed_characters=ALLOWED_CHARACTERS)))
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
                    name).handler
                stat = handler_stat_name_func(stat, max_length)
            return fn(_self, stat, *args, **kwargs)
        except InvalidStatsNameException:
            log.error('Invalid stat name: %s.', stat, exc_info=True)
            return None

    return cast(T, wrapper)


class AllowListValidatorProtocol(Protocol):
    def set_allow_list(
            self, allow_list: Optional[Union[Sequence[str], str]]) -> None:
        ...

    def test(self, stat: str) -> bool:
        ...


@register_plugin(plugin_type=PluginType.STATS_NAME_ALLOW_VALIDATOR,
                 plugin_name="default")
class DefaultAllowListValidator:
    """Class to filter unwanted stats"""

    def __init__(self, allow_list=None):
        self.allow_list = None
        self.set_allow_list(allow_list)

    def set_allow_list(
            self, allow_list: Optional[Union[Sequence[str], str]]) -> None:
        if allow_list:
            # pylint: disable=consider-using-generator
            if isinstance(allow_list, str):
                self.allow_list = tuple([item.strip().lower()
                                         for item in allow_list.split(',')])
        else:
            self.allow_list = None

    def test(self, stat: str) -> bool:
        """Test if stat is in the Allow List"""
        if self.allow_list is not None:
            return stat.strip().lower().startswith(self.allow_list)
        else:
            return True  # default is all metrics allowed


def get_current_allow_list_validator(
        name: Optional[str] = None) -> AllowListValidatorProtocol:
    name = name if name else "default"
    return get_plugin_instance(PluginType.STATS_NAME_ALLOW_VALIDATOR, name)


class BaseStatsdLogger:
    def __init__(
            self,
            statsd_client,
            stats_name_config: Optional[StatsNameConfig] = None,
            allow_name_validator_config: Optional[StatsAllowNameValidatorConfig] = None):
        self.statsd = statsd_client
        self.stats_name_config = None
        self.allow_name_validator_config = None
        self.allow_list_validator = None
        self.set_validator(stats_name_config, allow_name_validator_config)

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
            allow_validator_name)
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


@register_plugin(plugin_type=PluginType.STATS_LOGGER, plugin_name="statsd")
class SafeStatsdLogger(BaseStatsdLogger):
    """Statsd Logger"""

    def __init__(
            self,
            statsd_client,
            stats_name_config: Optional[StatsNameConfig] = None,
            allow_name_validator_config: Optional[StatsAllowNameValidatorConfig] = None):
        super().__init__(statsd_client, stats_name_config, allow_name_validator_config)

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


@register_plugin(plugin_type=PluginType.STATS_LOGGER, plugin_name="dog_statsd")
class SafeDogStatsdLogger(BaseStatsdLogger):
    """DogStatsd Logger"""

    def __init__(
            self,
            dog_statsd_client,
            stats_name_config: Optional[StatsNameConfig] = None,
            allow_name_validator_config: Optional[StatsAllowNameValidatorConfig] = None):
        super().__init__(
            dog_statsd_client,
            stats_name_config,
            allow_name_validator_config)

    @validate_stat
    def incr(self, stat, count=1, rate=1, tags=None):
        """Increment stat"""
        if self.allow_list_validator.test(stat):
            tags = tags or []
            return self.statsd_client.increment(
                metric=stat, value=count, tags=tags, sample_rate=rate)
        return None

    @validate_stat
    def decr(self, stat, count=1, rate=1, tags=None):
        """Decrement stat"""
        if self.allow_list_validator.test(stat):
            tags = tags or []
            return self.statsd_client.decrement(
                metric=stat, value=count, tags=tags, sample_rate=rate)
        return None

    @validate_stat
    def gauge(self, stat, value, rate=1, delta=False, tags=None):  # pylint: disable=unused-argument
        """Gauge stat"""
        if self.allow_list_validator.test(stat):
            tags = tags or []
            return self.statsd_client.gauge(
                metric=stat, value=value, tags=tags, sample_rate=rate)
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
            return Timer(
                self.statsd_client.timed(
                    stat,
                    *args,
                    tags=tags,
                    **kwargs))
        return Timer()


def get_current_stats_logger(
        name: Optional[str] = None) -> StatsLogger:
    name = name if name else "default"
    return get_plugin_instance(PluginType.STATS_LOGGER, name)
