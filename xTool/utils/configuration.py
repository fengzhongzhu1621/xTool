# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from __future__ import absolute_import

import os
import json
from tempfile import mkstemp
import copy
from collections import OrderedDict

import six
from six.moves import configparser
from six import iteritems
if six.PY3:
    ConfigParser = configparser.ConfigParser
else:
    ConfigParser = configparser.SafeConfigParser

from xTool.utils.helpers import expand_env_var
from xTool.utils.helpers import run_command
from xTool.utils.log.logging_mixin import LoggingMixin
from xTool.exceptions import XToolConfigException


log = LoggingMixin().log


def tmp_configuration_copy(conf):
    """将配置转换为json写入到临时文件
    Returns a path for a temporary file including a full copy of the configuration
    settings.
    :return: a path to a temporary file
    """
    cfg_dict = conf.as_dict(display_sensitive=True)
    temp_fd, cfg_path = mkstemp()

    # fdopen用于在一个已经打开的文件描述符上打开一个流，返回文件指针
    with os.fdopen(temp_fd, 'w') as temp_file:
        json.dump(cfg_dict, temp_file)

    return cfg_path


def read_config_file(file_path):
    """读取默认配置 ."""
    with open(file_path) as f:
        config = f.read()
        if six.PY2:
            config = config.decode('utf-8')
    return config


def parameterized_config(template):
    """
    Generates a configuration from the provided template + variables defined in
    current scope
    :param template: a config content templated with {{variables}}
    """
    all_vars = {k: v for d in [globals(), locals()] for k, v in d.items()}
    return template.format(**all_vars)


class XToolConfigParser(ConfigParser):

    # These configuration elements can be fetched as the stdout of commands
    # following the "{section}__{name}__cmd" pattern, the idea behind this
    # is to not store password on boxes in text files.
    as_command_stdout = {

    }

    def __init__(self, default_config=None, *args, **kwargs):
        super(XToolConfigParser, self).__init__(*args, **kwargs)
        # 读取格式化后的文件
        self.defaults = ConfigParser(*args, **kwargs)
        if default_config is not None:
            self.defaults.read_string(default_config)

        self.is_validated = False

    def read_string(self, string, source='<string>'):
        """
        Read configuration from a string.

        A backwards-compatible version of the ConfigParser.read_string()
        method that was introduced in Python 3.
        """
        # Python 3 added read_string() method
        if six.PY3:
            ConfigParser.read_string(self, string, source=source)
        # Python 2 requires StringIO buffer
        else:
            import StringIO
            self.readfp(StringIO.StringIO(string))

    def _validate(self):
        self.is_validated = True

    def _get_env_var_option(self, section, key):
        # must have format AIRFLOW__{SECTION}__{KEY} (note double underscore)
        env_var = 'XTOOL__{S}__{K}'.format(S=section.upper(), K=key.upper())
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
            if self.has_option(section, fallback_key):
                command = self.get(section, fallback_key)
                return run_command(command)

    def get(self, section, key, **kwargs):
        section = str(section).lower()
        key = str(key).lower()
        # 首先从环境变量中获取配置值，如果环境变量中存在，则不再从配置文件中获取
        option = self._get_env_var_option(section, key)
        if option is not None:
            return option

        # 然后从配置文件中获取
        if super(XToolConfigParser, self).has_option(section, key):
            # Use the parent's methods to get the actual config here to be able to
            # separate the config from default config.
            return expand_env_var(
                super(XToolConfigParser, self).get(section, key, **kwargs))

        # 执行表达式，获取结果
        option = self._get_cmd_option(section, key)
        if option:
            return option

        # ...then the default config
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
        """读取多个配置文件，并进行校验
        
        @note: 执行此函数，获取的配置项会覆盖掉构造函数中的默认配置 default_config
        """
        super(XToolConfigParser, self).read(filenames)
        self._validate()

    def has_option(self, section, option):
        try:
            # Using self.get() to avoid reimplementing the priority order
            # of config variables (env, config, cmd, defaults)
            self.get(section, option)
            return True
        except XToolConfigException:
            return False

    def remove_option(self, section, option, remove_default=True):
        """
        Remove an option if it exists in config from a file or
        default config. If both of config have the same option, this removes
        the option in both configs unless remove_default=False.
        """
        if super(XToolConfigParser, self).has_option(section, option):
            super(XToolConfigParser, self).remove_option(section, option)

        if self.defaults.has_option(section, option) and remove_default:
            self.defaults.remove_option(section, option)

    def getsection(self, section):
        """
        Returns the section as a dict. Values are converted to int, float, bool
        as required.
        :param section: section from the config
        :return: dict
        """
        if section not in self._sections and section not in self.defaults._sections:
            return None

        _section = copy.deepcopy(self.defaults._sections[section])

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

    def as_dict(self, display_source=False, display_sensitive=False):
        """
        Returns the current configuration as an OrderedDict of OrderedDicts.
        :param display_source: If False, the option value is returned. If True,
            a tuple of (option_value, source) is returned. Source is either
            'airflow.cfg' or 'default'.
        :type display_source: bool
        :param display_sensitive: If True, the values of options set by env
            vars and bash commands will be displayed. If False, those options
            are shown as '< hidden >'
        :type display_sensitive: bool
        """
        cfg = copy.deepcopy(self.defaults._sections)
        cfg.update(copy.deepcopy(self._sections))

        # remove __name__ (affects Python 2 only)
        for options in cfg.values():
            options.pop('__name__', None)

        # add source
        if display_source:
            for section in cfg:
                for k, v in cfg[section].items():
                    cfg[section][k] = (v, 'xTool config')

        # add env vars and overwrite because they have priority
        for ev in [ev for ev in os.environ if ev.startswith('XTOOL__')]:
            try:
                _, section, key = ev.split('__')
                opt = self._get_env_var_option(section, key)
            except ValueError:
                opt = None
            if opt:
                if (
                    not display_sensitive and
                        ev != 'XTOOL__CORE__UNIT_TEST_MODE'):
                    opt = '< hidden >'
                if display_source:
                    opt = (opt, 'env var')
                cfg.setdefault(section.lower(), OrderedDict()).update(
                    {key.lower(): opt})

        # add bash commands
        for (section, key) in self.as_command_stdout:
            opt = self._get_cmd_option(section, key)
            if opt:
                if not display_sensitive:
                    opt = '< hidden >'
                if display_source:
                    opt = (opt, 'bash cmd')
                cfg.setdefault(section, OrderedDict()).update({key: opt})

        return cfg
