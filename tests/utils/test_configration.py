#coding: utf-8

import os
import unittest

from xTool.utils.configuration import *


config_file_path = os.path.join(os.path.dirname(__file__), 'data', 'default_config.cfg')
product_config_file_path = os.path.join(os.path.dirname(__file__), 'data', 'product_config.cfg')
DEFAULT_CONFIG = read_config_file(config_file_path)

def test_read_config_file():
    default_config = parameterized_config(DEFAULT_CONFIG)
    assert 'smtp_host' in default_config


class TestXToolConfigParser(unittest.TestCase):
    def setUp(self):
        default_config = parameterized_config(DEFAULT_CONFIG)
        self.conf = XToolConfigParser(default_config=default_config)
        assert self.conf.is_validated is False
        assert self.conf.get('smtp', 'smtp_host') == 'localhost'
        self.conf.read(product_config_file_path)
        assert self.conf.is_validated is True
        assert self.conf.get('smtp', 'smtp_host') == 'localhost'
        assert self.conf.get('webserver', 'base_url') == 'http://localhost:8080'

    def test__get_env_var_option(self):
        actual = self.conf._get_env_var_option('smtp', 'smtp_host')
        assert actual is None
        os.environ['XTOOL__SMTP__SMTP_HOST'] = '0.0.0.0'
        actual = self.conf._get_env_var_option('smtp', 'smtp_host')
        assert actual == '0.0.0.0'
        assert self.conf.get('smtp', 'smtp_host') == '0.0.0.0'
        del os.environ['XTOOL__SMTP__SMTP_HOST']

    def test_get(self):
        assert self.conf.get('smtp', 'smtp_host') == 'localhost'
        assert self.conf.get('webserver', 'base_url') == 'http://localhost:8080'

    def test_getboolean(self):
        assert self.conf.getboolean('smtp', 'smtp_ssl') is False

    def test_getint(self):
        assert self.conf.getint('smtp', 'smtp_port') == 25

    def test_getfloat(self):
        assert self.conf.getint('smtp', 'smtp_port') == 25

    def test_has_option(self):
        assert self.conf.has_option('smtp', 'smtp_port') is True
        assert self.conf.has_option('smtp', 'smtp_port_error') is False

    def test_getsection(self):
        actual = self.conf.getsection('smtp')
        expected =  OrderedDict([
            ('smtp_host', 'localhost'),
            ('smtp_starttls', True),
            ('smtp_ssl', False),
            ('smtp_port', 25)])
        assert actual == expected

    def test_as_dict(self):
        actual = self.conf.as_dict()
        expected = OrderedDict([('smtp', OrderedDict([('smtp_host', 'localhost'), ('smtp_starttls', 'True'),('smtp_ssl', 'False'), ('smtp_port', '25')])), ('webserver', OrderedDict([('base_url', 'http://localhost:8080')]))])
        assert actual == expected


class XToolCmdOptionConfigParser(XToolConfigParser):
    as_command_stdout = {
        ('smtp', 'smtp_host'),
    }

class TestXToolConfigParser(unittest.TestCase):
    def setUp(self):
        default_config = parameterized_config(DEFAULT_CONFIG)
        default_config += os.linesep + "smtp_host_cmd = echo 1"
        self.conf = XToolCmdOptionConfigParser(default_config=default_config)
        assert self.conf.get('smtp', 'smtp_host_cmd') == 'echo 1'

    def test__get_cmd_option(self):
        assert self.conf.get('smtp', 'smtp_host') == '1' + os.linesep
        actual = self.conf._get_cmd_option('smtp', 'smtp_host')
        assert actual == '1' + os.linesep
