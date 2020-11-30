# -*- coding: utf-8 -*-

import importlib
import socket
import ipaddress

import netifaces

from xTool.compat import urlencode, urlparse, urlunparse, parse_qsl, unquote
from xTool.misc import tob
from xTool.exceptions import PortInvalidError


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

    net_address = netifaces.ifaddresses(dev_net)
    if netifaces.AF_INET in net_address:
        ip_address = net_address[netifaces.AF_INET][0]['addr']
    elif netifaces.AF_INET6 in net_address:
        ip_address = net_address[netifaces.AF_INET6][0]['addr']
    else:
        ip_address = ""
    return ip_address


def join_host_port(host: str, port: int) -> str:
    if ":" in host:
        # IPV6：带有端口号的IPV6地址字符串形式，地址部分应用"[]"括起来，在后面跟着":"带上端口号
        return '[' + host + ']:' + str(port)
    else:
        # IPV4
        return host + ':' + str(port)


def is_port_valid(port: int):
    if 0 <= int(port) <= 65535:
        return True
    else:
        return False


def is_unix_socket(port: int):
    if int(port) == 0:
        return True
    else:
        return False


def is_ip_v4(ip: str):
    try:
        addr4 = ipaddress.ip_address(ip)
    except ValueError:
        return False
    return addr4.version == 4


def is_ip_v6(ip: str):
    try:
        addr6 = ipaddress.ip_address(ip)
    except ValueError:
        return False
    return addr6.version == 6


def new_socket(ip: str, is_tcp: bool = True):
    sock = None
    if is_ip_v4(ip):
        sock = socket.socket(
            socket.AF_INET,
            socket.SOCK_STREAM if is_tcp else socket.SOCK_DGRAM)
    elif is_ip_v6(ip):
        sock = socket.socket(
            socket.AF_INET6,
            socket.SOCK_STREAM if is_tcp else socket.SOCK_DGRAM)
    return sock


def new_tcp_server_socket(ip: str, port: int, backlog=100, reuse_port=False):
    sock = new_socket(ip, is_tcp=True)
    # 用来控制是否开启Nagle算法，关闭Socket的缓冲,确保数据及时发送
    sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
    # 一般来说，一个端口释放后会等待两分钟之后才能再被使用，SO_REUSEADDR是让端口释放后立即就可以被再次使用
    # 用于对TCP套接字处于TIME_WAIT状态下的socket，才可以重复绑定使用
    # server程序总是应该在调用bind()之前设置SO_REUSEADDR套接字选项。TCP，先调用close()的一方会进入TIME_WAIT状态
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    if reuse_port:
        # 支持多个进程或者线程绑定到同一端口，提高服务器程序的吞吐性能
        # 允许多个套接字 bind()/listen() 同一个TCP/UDP端口
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
    sock.bind((ip, port))
    # backlog参数指定队列中最多可容纳的等待接受的传入连接数
    # 表示的是服务器拒绝(超过限制数量的)连接之前，操作系统可以挂起的最大连接数量。
    # 也可以看作是"排队的数量"
    sock.listen(backlog)
    sock.setblocking(False)
    return sock


def is_tcp_port_open(ip, port):
    """判断端口是否占用 ."""
    sock = None
    try:
        if not is_port_valid():
            raise PortInvalidError("端口%s无效" % ip)
        sock = new_socket(ip, is_tcp=True)
        # 出错时返回出错码,而不是抛出异常
        result = sock.connect_ex((ip, port))
        if result == 0:
            # 地址可以访问，说明端口已经被占用
            return False
        return True
    finally:
        if sock:
            sock.close()


def is_udp_port_open(ip, port):
    """判断端口是否占用 ."""
    sock = None
    try:
        if not is_port_valid():
            raise PortInvalidError("端口%s无效" % ip)
        sock = new_socket(ip, is_tcp=False)
        sock.bind((ip, port))
        return True
    except Exception as exc_info:  # pylint: disable=broad-except
        return False
    finally:
        if sock:
            sock.close()
