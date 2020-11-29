# -*- coding: utf-8 -*-

import importlib
import socket

import netifaces

from xTool.compat import urlencode, urlparse, urlunparse, parse_qsl, unquote
from xTool.misc import tob


def get_hostname(callable_path=None):
    """获得主机名 ."""
    if not callable_path:
        return socket.getfqdn()

    # Since we have a callable path, we try to import and run it next.
    # 根据配置文件中的设置的回调函数 module_path:attr_name 获取主机名
    # 加载指定模块，获得模块定义的主机属性名
    module_path, attr_name = callable_path.split(':')
    module = importlib.import_module(module_path)
    func = getattr(module, attr_name)
    # 执行属性方法返回结果
    return func()


def parse_netloc_to_hostname(uri_parts):
    """获得urlparse解析后的主机名
    Python automatically converts all letters to lowercase in hostname
    See: https://issues.apache.org/jira/browse/AIRFLOW-3615
    """
    hostname = unquote(uri_parts.hostname or '')
    if '/' in hostname:
        hostname = uri_parts.netloc
        if "@" in hostname:
            hostname = hostname.rsplit("@", 1)[1]
        if ":" in hostname:
            hostname = hostname.split(":", 1)[0]
        hostname = unquote(hostname)
    return hostname


def int2ip(ipnum):
    seg1 = int(ipnum / 16777216) % 256
    seg2 = int(ipnum / 65536) % 256
    seg3 = int(ipnum / 256) % 256
    seg4 = int(ipnum) % 256
    return '{}.{}.{}.{}'.format(seg1, seg2, seg3, seg4)


def ip2int(ip):
    seg0, seg1, seg2, seg3 = (int(seg) for seg in ip.split('.'))
    res = (16777216 * seg0) + (65536 * seg1) + (256 * seg2) + seg3
    return res


def url_concat(url, args):
    """Concatenate url and arguments regardless of whether
    url has existing query parameters.

    ``args`` may be either a dictionary or a list of key-value pairs
    (the latter allows for multiple values with the same key.

    >>> url_concat("http://example.com/foo", dict(c="d"))
    'http://example.com/foo?c=d'
    >>> url_concat("http://example.com/foo?a=b", dict(c="d"))
    'http://example.com/foo?a=b&c=d'
    >>> url_concat("http://example.com/foo?a=b", [("c", "d"), ("c", "d2")])
    'http://example.com/foo?a=b&c=d&c=d2'
    """
    if args is None:
        return url
    parsed_url = urlparse(url)
    if isinstance(args, dict):
        parsed_query = parse_qsl(parsed_url.query, keep_blank_values=True)
        parsed_query.extend(args.items())
    elif isinstance(args, list) or isinstance(args, tuple):
        parsed_query = parse_qsl(parsed_url.query, keep_blank_values=True)
        parsed_query.extend(args)
    else:
        err = "'args' parameter should be dict, list or tuple. Not {0}".format(
            type(args))
        raise TypeError(err)
    final_query = urlencode(parsed_query)
    url = urlunparse((
        parsed_url[0],
        parsed_url[1],
        parsed_url[2],
        parsed_url[3],
        final_query,
        parsed_url[5]))
    return url


def get_local_host_ip(ifname=b'eth1', ip: str = None, port: int = None):
    """获得本机的IP地址 ."""
    import platform
    import socket
    if not ifname and ip and port:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect((ip, port))
            return s.getsockname()[0]
        finally:
            s.close()
    if platform.system() == 'Linux':
        import fcntl
        import struct
        ifname = tob(ifname)
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            o_ip = socket.inet_ntoa(fcntl.ioctl(
                s.fileno(),
                0x8915,
                struct.pack('256s', ifname[:15])
            )[20:24])
        finally:
            s.close()
    else:
        o_ip = socket.gethostbyname(socket.gethostname())
    return o_ip


def find_internal_ip_on_device_network(dev_net: str):
    if not dev_net:
        return ""
    if dev_net not in netifaces.interfaces():
        return ""
    ip_address = ""
    net_address = netifaces.ifaddresses(dev_net)
    if netifaces.AF_INET in net_address:
        ip_address = net_address[netifaces.AF_INET][0]['addr']
    elif netifaces.AF_INET6 in net_address:
        ip_address = net_address[netifaces.AF_INET6][0]['addr']

    return ip_address
