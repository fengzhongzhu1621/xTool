# -*- coding: utf-8 -*-

from __future__ import absolute_import
# 开启除法浮点运算
from __future__ import division
from __future__ import print_function
# 把你当前模块所有的字符串（string literals）转为unicode
from __future__ import unicode_literals

import os
import json
from tempfile import mkstemp
from base64 import b64encode
from builtins import str
import copy
from collections import OrderedDict
import warnings
import types

from future import standard_library
import six
from six import iteritems

from six.moves import configparser
if six.PY3:
    ConfigParser = configparser.ConfigParser
else:
    ConfigParser = configparser.SafeConfigParser

from xTool.utils.helpers import expand_env_var
from xTool.utils.helpers import run_command
from xTool.utils.helpers import strtobool
from xTool.utils.log.logging_mixin import LoggingMixin
from xTool.utils.module_loading import import_string_from_package
from xTool.exceptions import (XToolConfigException, PyFileError)
from xTool.misc import USE_WINDOWS


standard_library.install_aliases()

log = LoggingMixin().log


def read_config_file(file_path):
    """根据文件路径，读取文件内容 ."""
    if six.PY2:
        with open(file_path) as f:
            config = f.read()
            return config.decode('utf-8')
    else:
        with open(file_path, encoding='utf-8') as f:
            return f.read()


def parameterized_config(template):
    """使用全局变量和局部变量渲染模版字符串
    Generates a configuration from the provided template + variables defined in
    current scope
    :param template: a config content templated with {{variables}}
    """
    all_vars = {k: v for d in [globals(), locals()] for k, v in iteritems(d)}
    return template.format(**all_vars)


def tmp_configuration_copy(cfg_dict, chmod=0o600):
    """将配置字典复制到临时文件中，并返回临时文件的路径 ."""
    # 创建临时文件
    temp_fd, cfg_path = mkstemp()
    # 写临时文件
    with os.fdopen(temp_fd, 'w') as temp_file:
        if chmod is not None:
            if not USE_WINDOWS:
                os.fchmod(temp_fd, chmod)
        # 将json数据写入到临时文件
        json.dump(cfg_dict, temp_file)
    # 返回临时文件的路径
    return cfg_path


class XToolConfigParser(ConfigParser):
    """通用配置文件解析器 .

    Args:
        default_config: 默认.ini格式配置文件的内容

    examples:
        # 创建配置对象，读取默认配置
        conf = XToolConfigParser(default_config=parameterized_config(DEFAULT_CONFIG))
        # 读取正式环境配置文件，覆盖默认配置
        conf.read(AIRFLOW_CONFIG)
    """
    env_prefix = "XTOOL"

    # These configuration elements can be fetched as the stdout of commands
    # following the "{section}__{name}__cmd" pattern, the idea behind this
    # is to not store password on boxes in text files.
    as_command_stdout = {}

    deprecated_options = {}

    # 过期配置警告模版
    deprecation_format_string = (
        'The {old} option in [{section}] has been renamed to {new} - the old '
        'setting has been used, but please update your config.'
    )

    def __init__(self, default_config=None, *args, **kwargs):
        super(XToolConfigParser, self).__init__(*args, **kwargs)
        # 创建默认配置文件解析器
        self.defaults = ConfigParser(*args, **kwargs)
        # 从字符串读取默认配置
        if default_config is not None:
            self.defaults.read_string(default_config)

        self.is_validated = False

    def _validate(self):
        """添加配置验证逻辑 ."""
        self.is_validated = True

    def _get_env_var_option(self, section, key):
        """从环境变量中获取配置的值，
        把环境变量的值中包含的”~”和”~user”转换成用户目录，并获取配置结果值 ."""
        # must have format XTOOL__{SECTION}__{KEY} (note double underscore)
        env_var = '{E}__{S}__{K}'.format(
            E=self.env_prefix, S=section.upper(), K=key.upper())
        if env_var in os.environ:
            return expand_env_var(os.environ[env_var])

    def _get_cmd_option(self, section, key):
        """从配置项中获取指令，并执行指令获取指令执行后的返回值

            - 如果key不存在_cmd结尾，则获取key的值
            - 如果key没有配置 且 key以_cmd结尾，则获取key的值，并执行值表示的表达式，返回表达式的结果
        """
        fallback_key = key + '_cmd'
        # if this is a valid command key...
        if (section, key) in self.as_command_stdout:
            # 如果用户自定义配置中存在以"_cmd"结尾的配置值
            # 则执行此配置值的shell命令，获取其返回值作为真正的配置项的值
            if super(XToolConfigParser, self) \
                    .has_option(section, fallback_key):
                command = super(XToolConfigParser, self) \
                    .get(section, fallback_key)
                # 执行shell命令，返回标准输出（Unicode编码）
                return run_command(command)

    def get(self, section, key, **kwargs):
        """返回配置值 ."""
        section = str(section).lower()
        key = str(key).lower()

        # 1. 首先从环境变量中获取配置值，如果环境变量中存在，则不再从配置文件中获取
        #    过期的配置输出告警，并返回配置值
        option = self._get_env_var_option(section, key)
        if option is not None:
            return option
        deprecated_name = self.deprecated_options.get(section, {}).get(key)
        if deprecated_name:
            option = self._get_env_var_option(section, deprecated_name)
            if option is not None:
                self._warn_deprecate(section, key, deprecated_name)
                return option
        # 2. 从用户自定义配置文件中获取
        if super(XToolConfigParser, self).has_option(section, key):
            return expand_env_var(
                super(XToolConfigParser, self).get(section, key, **kwargs))
        if deprecated_name:
            if super(
                    XToolConfigParser,
                    self).has_option(
                    section,
                    deprecated_name):
                self._warn_deprecate(section, key, deprecated_name)
                return expand_env_var(super(XToolConfigParser, self).get(
                    section,
                    deprecated_name,
                    **kwargs
                ))
        # 3. 获得带有_cmd后缀的配置，执行表达式，获取结果
        option = self._get_cmd_option(section, key)
        if option:
            return option
        if deprecated_name:
            option = self._get_cmd_option(section, deprecated_name)
            if option:
                self._warn_deprecate(section, key, deprecated_name)
                return option
        # 4. 从默认配置文件中获取
        if self.defaults.has_option(section, key):
            return expand_env_var(
                self.defaults.get(section, key, **kwargs))
        else:
            log.warning(
                "section/key [{section}/{key}] not found in config".format(**locals())
            )
            # 配置不存在，抛出异常
            raise XToolConfigException(
                "section/key [{section}/{key}] not found "
                "in config".format(**locals()))

    def getboolean(self, section, key):
        val = str(self.get(section, key)).lower().strip()
        # 去掉结尾的注释
        if '#' in val:
            val = val.split('#')[0].strip()
        if val.lower() in ('t', 'true', '1'):
            return True
        elif val.lower() in ('f', 'false', '0'):
            return False
        else:
            raise XToolConfigException(
                'The value for configuration option "{}:{}" is not a '
                'boolean (received "{}").'.format(section, key, val))

    def getint(self, section, key):
        return int(self.get(section, key))

    def getfloat(self, section, key):
        return float(self.get(section, key))

    def read(self, filenames):
        """读取多个最新的配置文件，进行校验，并覆盖默认配置."""
        super(XToolConfigParser, self).read(filenames)
        self._validate()

    def read_dict(self, *args, **kwargs):
        """从字典中获取配置 ."""
        super(XToolConfigParser, self).read_dict(*args, **kwargs)
        self._validate()

    def has_option(self, section, option):
        """判断配置是否存在 ."""
        try:
            # Using self.get() to avoid reimplementing the priority order
            # of config variables (env, config, cmd, defaults)
            self.get(section, option)
            return True
        except XToolConfigException:
            return False

    def remove_option(self, section, option, remove_default=True):
        """删除配置 ."""
        # 删除用户自定义配置
        if super(XToolConfigParser, self).has_option(section, option):
            super(XToolConfigParser, self).remove_option(section, option)
        # 删除默认配置
        if self.defaults.has_option(section, option) and remove_default:
            self.defaults.remove_option(section, option)

    def getsection(self, section):
        """根据配置段名获得所有的配置项 ."""
        # 判断配置端是否存在
        if section not in self._sections and section not in self.defaults._sections:
            return None

        # 复制默认配置端的内容
        _section = copy.deepcopy(self.defaults._sections[section])

        # 使用用户自定义配置端更新默认配置端
        if section in self._sections:
            _section.update(copy.deepcopy(self._sections[section]))

        # 遍历section下所有的key，对value进行格式化处理
        for key, val in iteritems(_section):
            try:
                val = int(val)
            except ValueError:
                try:
                    val = float(val)
                except ValueError:
                    if val.lower() in ('t', 'true'):
                        val = True
                    elif val.lower() in ('f', 'false'):
                        val = False
            _section[key] = val
        return _section

    def as_dict(
            self, display_sensitive=False, raw=False):
        """将配置文件转换为配置字典 ."""
        cfg = {}
        configs = (
            self.defaults,       # 默认配置文件解析器
            self,                # 用户自定义配置文件解析器
        )

        # 遍历所有配置端，将配置文件转换为字典格式
        for parser in configs:
            for section in parser.sections():
                # 将配置端保存到有序字典
                sect = cfg.setdefault(section, OrderedDict())
                # items(self, section, raw=False, vars=None)
                #     - 在raw为true的情况下，忽略%的替换语法，直接输出
                #     - 在raw为false的情况下，vars中包含要替换的key，%语法中的内容被替换
                for (k, val) in parser.items(section=section, raw=raw):
                    sect[k] = val

        # 用户环境变量的配置覆盖配置文件的配置，环境变量有较高的优先级
        for ev in [
            ev for ev in os.environ if ev.startswith(
                '%s__' %
                self.env_prefix)]:
            try:
                _, section, key = ev.split('__')
                # 从环境变量中获取配置的值
                opt = self._get_env_var_option(section, key)
            except ValueError:
                continue
            if (not display_sensitive and ev !=
                    '%s__CORE__UNIT_TEST_MODE' % self.env_prefix):
                opt = '< hidden >'
            elif raw:
                opt = opt.replace('%', '%%')
            cfg.setdefault(section.lower(), OrderedDict()).update(
                {key.lower(): opt})

        # add bash commands
        for (section, key) in self.as_command_stdout:
            # 从shell命令中获得配置项的值
            opt = self._get_cmd_option(section, key)
            if opt:
                if not display_sensitive:
                    opt = '< hidden >'
                elif raw:
                    opt = opt.replace('%', '%%')
                cfg.setdefault(section, OrderedDict()).update({key: opt})
                # 去掉bash命令
                del cfg[section][key + '_cmd']

        return cfg

    def _warn_deprecate(self, section, key, deprecated_name):
        """输出过期配置警告信息 ."""
        warnings.warn(
            self.deprecation_format_string.format(
                old=deprecated_name,
                new=key,
                section=section,
            ),
            DeprecationWarning,
            stacklevel=3,
        )


DEFAULT_CONFIG = {
    "REQUEST_MAX_SIZE": 100000000,  # 100 megabytes
    "REQUEST_BUFFER_QUEUE_SIZE": 100,
    "REQUEST_TIMEOUT": 60,  # 60 seconds
    "RESPONSE_TIMEOUT": 60,  # 60 seconds
    "KEEP_ALIVE": True,
    "KEEP_ALIVE_TIMEOUT": 5,  # 5 seconds
    "WEBSOCKET_MAX_SIZE": 2 ** 20,  # 1 megabyte
    "WEBSOCKET_MAX_QUEUE": 32,
    "WEBSOCKET_READ_LIMIT": 2 ** 16,
    "WEBSOCKET_WRITE_LIMIT": 2 ** 16,
    "GRACEFUL_SHUTDOWN_TIMEOUT": 15.0,  # 15 sec
    "ACCESS_LOG": True,
    "FORWARDED_SECRET": None,
    "REAL_IP_HEADER": None,
    "PROXIES_COUNT": None,
    "FORWARDED_FOR_HEADER": "X-Forwarded-For",
}


BASE_LOGO = """

                 XTool

"""


class Config(dict):
    def __init__(self, defaults=None, load_env=True, keep_alive=None, base_logo=None, prefix="XTOOL_"):
        defaults = defaults or {}
        super().__init__({**DEFAULT_CONFIG, **defaults})

        self.LOGO = base_logo if base_logo else BASE_LOGO
        self.prefix = prefix

        if keep_alive is not None:
            self.KEEP_ALIVE = keep_alive

        if load_env:
            prefix = self.prefix if load_env is True else load_env
            self.load_environment_vars(prefix=prefix)

    def __getattr__(self, attr):
        try:
            return self[attr]
        except KeyError as ke:
            raise AttributeError(f"Config has no '{ke.args[0]}'")

    def __setattr__(self, attr, value):
        self[attr] = value

    def from_envvar(self, variable_name):
        """Load a configuration from an environment variable pointing to
        a configuration file.

        :param variable_name: name of the environment variable
        :return: bool. ``True`` if able to load config, ``False`` otherwise.
        """
        # 从环境变量中获取配置文件的路径
        config_file = os.environ.get(variable_name)
        if not config_file:
            raise RuntimeError(
                "The environment variable %r is not set and "
                "thus configuration could not be loaded." % variable_name
            )
        return self.from_pyfile(config_file)

    def from_pyfile(self, filename):
        """Update the values in the config from a Python file.
        Only the uppercase variables in that module are stored in the config.

        :param filename: an absolute path to the config file
        """
        module = types.ModuleType("config")
        module.__file__ = filename
        try:
            with open(filename) as config_file:
                exec(  # nosec
                    compile(config_file.read(), filename, "exec"),
                    module.__dict__,
                )
        except IOError as e:
            e.strerror = "Unable to load configuration file (%s)" % e.strerror
            raise
        except Exception as e:
            raise PyFileError(filename) from e

        # 从创建的对象中加载配置
        self.from_object(module)
        return True

    def from_object(self, obj):
        """Update the values from the given object.
        Objects are usually either modules or classes.

        Just the uppercase variables in that object are stored in the config.
        Example usage::

            from yourapplication import default_config
            app.config.from_object(default_config)

            or also:
            app.config.from_object('myproject.config.MyConfigClass')

        You should not use this function to load the actual configuration but
        rather configuration defaults. The actual config should be loaded
        with :meth:`from_pyfile` and ideally from a location not within the
        package because the package might be installed system wide.

        :param obj: an object holding the configuration
        """
        if isinstance(obj, str):
            obj = import_string_from_package(obj)
        for key in dir(obj):
            if key.isupper():
                self[key] = getattr(obj, key)

    def load_environment_vars(self, prefix=None):
        """
        Looks for prefixed environment variables and applies
        them to the configuration if present.
        """
        if not prefix:
            prefix = self.prefix
        for k, v in os.environ.items():
            if k.startswith(prefix):
                _, config_key = k.split(prefix, 1)
                try:
                    self[config_key] = int(v)
                except ValueError:
                    try:
                        self[config_key] = float(v)
                    except ValueError:
                        try:
                            self[config_key] = strtobool(v)
                        except ValueError:
                            self[config_key] = v
