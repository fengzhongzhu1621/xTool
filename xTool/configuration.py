# -*- coding: utf-8 -*-
#
from __future__ import absolute_import
# 开启除法浮点运算
from __future__ import division
from __future__ import print_function
# 把你当前模块所有的字符串（string literals）转为unicode
from __future__ import unicode_literals

import copy
import errno
import os
import six
import subprocess
import warnings
import shlex
import sys
from tempfile import mkstemp

from future import standard_library

from six import iteritems

from xTool.utils.log.logging_mixin import LoggingMixin

standard_library.install_aliases()

from builtins import str
from collections import OrderedDict
from six.moves import configparser

from xTool.exceptions import XToolConfigException

log = LoggingMixin().log

# show Airflow's deprecation warnings
warnings.filterwarnings(
    action='default', category=DeprecationWarning, module='xTool')
warnings.filterwarnings(
    action='default', category=PendingDeprecationWarning, module='xTool')

if six.PY3:
    ConfigParser = configparser.ConfigParser
else:
    ConfigParser = configparser.SafeConfigParser


def generate_fernet_key():
    try:
        from cryptography.fernet import Fernet
    except ImportError:
        pass
    try:
        # 产生了一个32位随机数，并用base64编码，并解码为unicode编码
        key = Fernet.generate_key().decode()
    except NameError:
        key = "cryptography_not_found_storing_passwords_in_plain_text"
    return key


def expand_env_var(env_var):
    """
    Expands (potentially nested) env vars by repeatedly applying
    `expandvars` and `expanduser` until interpolation stops having
    any effect.
    """
    if not env_var:
        return env_var
    while True:
        # 1. 根据环境变量替换env_var
        # 2. 把env_var中包含的”~”和”~user”转换成用户目录
        interpolated = os.path.expanduser(os.path.expandvars(str(env_var)))
        if interpolated == env_var:
            return interpolated
        else:
            env_var = interpolated


def run_command(command):
    """
    Runs command and returns stdout
    """
    process = subprocess.Popen(
        shlex.split(command),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        close_fds=True)
    output, stderr = [stream.decode(sys.getdefaultencoding(), 'ignore')
                      for stream in process.communicate()]

    if process.returncode != 0:
        raise XToolConfigException(
            "Cannot execute {}. Error code is: {}. Output: {}, Stderr: {}"
            .format(command, process.returncode, output, stderr)
        )

    return output


# 读取默认配置
_templates_dir = os.path.join(os.path.dirname(__file__), 'config_templates')
with open(os.path.join(_templates_dir, 'default_xTool.cfg')) as f:
    DEFAULT_CONFIG = f.read()
with open(os.path.join(_templates_dir, 'default_test.cfg')) as f:
    TEST_CONFIG = f.read()


class XToolConfigParser(ConfigParser):

    # These configuration elements can be fetched as the stdout of commands
    # following the "{section}__{name}__cmd" pattern, the idea behind this
    # is to not store password on boxes in text files.
    as_command_stdout = {
        ('core', 'sql_alchemy_conn'),
        ('core', 'fernet_key'),
        ('celery', 'broker_url'),
        ('celery', 'result_backend')
    }

    def __init__(self, *args, **kwargs):
        ConfigParser.__init__(self, *args, **kwargs)
        # 读取格式化后的文件
        self.read_string(parameterized_config(DEFAULT_CONFIG))
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
        # if this is a valid command key...
        if (section, key) in XToolConfigParser.as_command_stdout:
            # if the original key is present, return it no matter what
            if self.has_option(section, key):
                return ConfigParser.get(self, section, key)

            fallback_key = key + '_cmd'
            # otherwise, execute the fallback key
            if self.has_option(section, fallback_key):
                command = self.get(section, fallback_key)
                return run_command(command)

    def get(self, section, key, **kwargs):
        section = str(section).lower()
        key = str(key).lower()

        # 首先从环境变量中获取配置值，如果环境变量中存在，则不再从配置文件中获取
        # first check environment variables
        option = self._get_env_var_option(section, key)
        if option is not None:
            return option

        # 然后从配置文件中获取
        # ...then the config file
        if self.has_option(section, key):
            return expand_env_var(
                ConfigParser.get(self, section, key, **kwargs))

        # ...then commands
        # 执行表达式，获取结果
        option = self._get_cmd_option(section, key)
        if option:
            return option

        else:
            log.warning(
                "section/key [{section}/{key}] not found in config".format(**locals())
            )

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
        """读取多个配置文件，并进行校验 ."""
        ConfigParser.read(self, filenames)
        self._validate()

    def getsection(self, section):
        """
        Returns the section as a dict. Values are converted to int, float, bool
        as required.
        :param section: section from the config
        :return: dict
        """
        if section in self._sections:
            _section = self._sections[section]
            # 遍历section下所有的key，对value进行格式化处理
            for key, val in iteritems(self._sections[section]):
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

        return None

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
        cfg = copy.deepcopy(self._sections)

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
                        not display_sensitive
                        and ev != 'XTOOL__CORE__UNIT_TEST_MODE'):
                    opt = '< hidden >'
                if display_source:
                    opt = (opt, 'env var')
                cfg.setdefault(section.lower(), OrderedDict()).update(
                    {key.lower(): opt})

        # add bash commands
        for (section, key) in XToolConfigParser.as_command_stdout:
            opt = self._get_cmd_option(section, key)
            if opt:
                if not display_sensitive:
                    opt = '< hidden >'
                if display_source:
                    opt = (opt, 'bash cmd')
                cfg.setdefault(section, OrderedDict()).update({key: opt})

        return cfg

    def load_test_config(self):
        """
        Load the unit test configuration.

        Note: this is not reversible.
        """
        # override any custom settings with defaults
        self.read_string(parameterized_config(DEFAULT_CONFIG))
        # then read test config
        self.read_string(parameterized_config(TEST_CONFIG))
        # then read any "custom" test settings
        self.read(TEST_CONFIG_FILE)


def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError as exc:  # Python >2.5
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise XToolConfigException(
                'Error creating {}: {}'.format(path, exc.strerror))

# Setting AIRFLOW_HOME and AIRFLOW_CONFIG from environment variables, using
# "~/airflow" and "~/airflow/airflow.cfg" respectively as defaults.


if 'XTOOL_HOME' not in os.environ:
    XTOOL_HOME = expand_env_var('~/xTool')
else:
    XTOOL_HOME = expand_env_var(os.environ['XTOOL_HOME'])

mkdir_p(XTOOL_HOME)

if 'XTOOL_CONFIG' not in os.environ:
    if os.path.isfile(expand_env_var('~/xTool.cfg')):
        XTOOL_CONFIG = expand_env_var('~/xTool.cfg')
    else:
        XTOOL_CONFIG = XTOOL_HOME + '/xTool.cfg'
else:
    XTOOL_CONFIG = expand_env_var(os.environ['XTOOL_CONFIG'])


def parameterized_config(template):
    """
    Generates a configuration from the provided template + variables defined in
    current scope
    :param template: a config content templated with {{variables}}
    """
    all_vars = {k: v for d in [globals(), locals()] for k, v in d.items()}
    return template.format(**all_vars)


TEST_CONFIG_FILE = XTOOL_HOME + '/unittests.cfg'

# only generate a Fernet key if we need to create a new config file
if not os.path.isfile(TEST_CONFIG_FILE) or not os.path.isfile(XTOOL_CONFIG):
    FERNET_KEY = generate_fernet_key()
else:
    FERNET_KEY = ''

log.info("Reading the config from %s", XTOOL_CONFIG)

conf = XToolConfigParser()
conf.read(XTOOL_CONFIG)


def load_test_config():
    """
    Load the unit test configuration.

    Note: this is not reversible.
    """
    conf.load_test_config()


if conf.getboolean('core', 'unit_test_mode'):
    load_test_config()


def get(section, key, **kwargs):
    return conf.get(section, key, **kwargs)


def getboolean(section, key):
    return conf.getboolean(section, key)


def getfloat(section, key):
    return conf.getfloat(section, key)


def getint(section, key):
    return conf.getint(section, key)


def getsection(section):
    return conf.getsection(section)


def has_option(section, key):
    return conf.has_option(section, key)


def remove_option(section, option):
    return conf.remove_option(section, option)


def as_dict(display_source=False, display_sensitive=False):
    return conf.as_dict(
        display_source=display_source, display_sensitive=display_sensitive)


as_dict.__doc__ = conf.as_dict.__doc__


def set(section, option, value):  # noqa
    return conf.set(section, option, value)


def tmp_configuration_copy(copy_sections):
    """拷贝配置文件到临时文件中
    Returns a path for a temporary file including a full copy of the configuration
    settings.
    :param copy_sections: 需要备份的section
    :return: a path to a temporary file
    """
    cfg_dict = conf.as_dict(display_sensitive=True)
    temp_fd, cfg_path = mkstemp()

    cfg_subset = dict()
    for section in copy_sections:
        cfg_subset[section] = cfg_dict.get(section, {})

    with os.fdopen(temp_fd, 'w') as temp_file:
        json.dump(cfg_subset, temp_file)

    return cfg_path