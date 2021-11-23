# -*- coding: utf-8 -*-

import importlib
import socket
import ipaddress
import struct
import netifaces

from xTool.compat import (
    urlencode,
    urlparse,
    urlunparse,
    parse_qsl,
    unquote)
from xTool.misc import tob, OS_IS_WINDOWS
from xTool.exceptions import PortInvalidError


DEFAULT_BACKLOG = 1500


def get_hostname(callable_path=None) -> str:
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


def get_local_host_ip(ifname=b'eth1', ip: str = None, port: int = None) -> str:
    """获得本机的IP地址 ."""
    import platform
    import socket
    if not ifname and ip and port:
        sock = None
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.connect((ip, port))
            return sock.getsockname()[0]
        finally:
            if sock:
                sock.close()
    if platform.system() == 'Linux':
        import fcntl
        import struct
        ifname = tob(ifname)
        sock = None
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            o_ip = socket.inet_ntoa(fcntl.ioctl(
                sock.fileno(),
                0x8915,
                struct.pack('256s', ifname[:15])
            )[20:24])
        finally:
            sock.close()
    else:
        o_ip = socket.gethostbyname(socket.gethostname())
    return o_ip


def find_internal_ip_on_device_network(dev_net: str) -> str:
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


def join_address(host: str, port: int) -> str:
    if ":" in host:
        # IPV6：带有端口号的IPV6地址字符串形式，地址部分应用"[]"括起来，在后面跟着":"带上端口号
        return "[{}]:{}".format(host, port)
    else:
        # IPV4
        return "{}:{}".format(host, port)


def is_port_valid(port: int) -> bool:
    if 0 <= int(port) <= 65535:
        return True
    else:
        return False


def is_unix_socket(port: int) -> bool:
    if int(port) == 0:
        return True
    else:
        return False


def is_ipv4_deprecated(ip: str) -> bool:
    try:
        addr4 = ipaddress.ip_address(ip)
    except ValueError:
        return False
    return addr4.version == 4


def is_ipv6_deprecated(ip: str) -> bool:
    try:
        addr6 = ipaddress.ip_address(ip)
    except ValueError:
        return False
    return addr6.version == 6


def is_ipv4(ip: str) -> bool:
    try:
        # 将点分文本的IP地址转换为二进制网络字节序”的IP地址
        socket.inet_pton(socket.AF_INET, ip)
    except socket.error:
        return False
    return True


def is_ipv6(ip: str) -> bool:
    """判断IP是否为ipv6, 比使用ipaddress性能更高 ."""
    try:
        # 将点分文本的IP地址转换为二进制网络字节序”的IP地址
        socket.inet_pton(socket.AF_INET6, ip)
    except socket.error:
        return False
    return True


def is_tcp_port_open(ip, port) -> bool:
    """判断端口是否占用 ."""
    sock = None
    try:
        if not is_port_valid(port):
            raise PortInvalidError("端口%s无效" % ip)
        sock = new_socket(ip, stream=True)
        # 出错时返回出错码,而不是抛出异常
        result = sock.connect_ex((ip, port))
        if result == 0:
            # 地址可以访问，说明端口已经被占用
            return False
        return True
    finally:
        if sock:
            sock.close()


def is_udp_port_open(ip, port) -> bool:
    """判断端口是否占用 ."""
    sock = None
    try:
        if not is_port_valid(port):
            raise PortInvalidError("端口%s无效" % ip)
        sock = new_socket(ip, stream=False)
        sock.bind((ip, port))
        return True
    except Exception:  # pylint: disable=broad-except
        return False
    finally:
        if sock:
            sock.close()


def ipv4_to_bytes(ip):
    return socket.inet_pton(socket.AF_INET, ip)


def bytes_to_ipv4(ip_bytes):
    return socket.inet_ntop(socket.AF_INET, ip_bytes)


def ipv6_to_bytes(ip):
    return socket.inet_pton(socket.AF_INET6, ip)


def bytes_to_ipv6(ip_bytes):
    return socket.inet_ntop(socket.AF_INET6, ip_bytes)


def ipv4_to_int(ip):
    return struct.unpack("!L", socket.inet_aton(ip))[0]


def int_to_ipv4(ip_num):
    return socket.inet_ntoa(struct.pack('!L', ip_num))


def ipv6_to_long(ipv6):
    hi, lo = struct.unpack('!QQ', socket.inet_pton(socket.AF_INET6, ipv6))
    return (hi << 64) | lo


def long_to_ipv6(ip_num):
    return socket.inet_ntop(
        socket.AF_INET6,
        struct.pack(
            '!QQ',
            ip_num >> 64,
            ip_num & 0xffffffffffffffff))


def ip_to_bytes(ip):
    if is_ipv4(ip):
        return ipv4_to_bytes(ip)
    elif is_ipv6(ip):
        return ipv6_to_bytes(ip)


def bytes_to_ip(ip_bytes):
    if len(ip_bytes) == 4:
        return bytes_to_ipv4(ip_bytes)
    elif len(ip_bytes) == 16:
        return bytes_to_ipv6(ip_bytes)


def get_unused_port() -> int:
    sock = socket.socket()
    sock.bind(("", 0))
    port = sock.getsockname()[-1]
    sock.close()
    return port


def new_socket(ip: str, stream: bool = True) -> socket.socket:
    sock = None
    if is_ipv4(ip):
        sock = socket.socket(
            socket.AF_INET,
            socket.SOCK_STREAM if stream else socket.SOCK_DGRAM)
    elif is_ipv6(ip):
        sock = socket.socket(
            socket.AF_INET6,
            socket.SOCK_STREAM if stream else socket.SOCK_DGRAM)
    return sock


def new_inet_socket(ip: str, port: int, backlog=100, reuse_port=False, stream=True) -> socket.socket:
    sock = new_socket(ip, stream=stream)
    if stream:
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
    if stream:
        # backlog参数指定队列中最多可容纳的等待接受的传入连接数
        # 表示的是服务器拒绝(超过限制数量的)连接之前，操作系统可以挂起的最大连接数量。
        # 也可以看作是"排队的数量"
        sock.listen(backlog)
    sock.setblocking(False)
    return sock


def new_tcp_socket(ip: str, port: int, backlog=DEFAULT_BACKLOG, reuse_port=False) -> socket.socket:
    sock = new_inet_socket(ip, port, backlog=backlog, reuse_port=reuse_port, stream=True)
    return sock


def new_udp_socket(ip: str, port: int, backlog=DEFAULT_BACKLOG, reuse_port=False) -> socket.socket:
    sock = new_inet_socket(ip, port, backlog=backlog, reuse_port=reuse_port, stream=False)
    return sock


def new_unix_socket(ip: str, backlog=DEFAULT_BACKLOG) -> socket.socket:
    sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    sock.bind(ip)
    sock.listen(backlog)
    sock.setblocking(False)
    return sock


def new_socketpair():
    if OS_IS_WINDOWS:
        socket_pair = socket.socketpair()
    else:
        # 使用 socketpair 实现进程间通信
        # 创建了一对无名的套接字描述符（只能在AF_UNIX域中使用），描述符存储于一个二元数组,eg. s[2] .
        # 这对套接字可以进行双工通信，每一个描述符既可以读也可以写。
        # 这个在同一个进程中也可以进行通信，向s[0]中写入，就可以从s[1]中读取（只能从 s[1]中读取），也可以在s[1]中写入，然后从s[0]中读取；
        # 但是，若没有在0端写入，而从1端读取，则1端的读取操作会阻塞，即使在1端写入，也 不能从1读取，仍然阻塞；反之亦然
        #
        # AF_UNIX 指的就是 Unix Domain socket，同一台机器上不同进程间的通信机制
        # 只支持 AF_LOCAL 或者 AF_UNIX，不支持 TCP/IP，也就是 AF_INET， 所以用 socketpair() 的话无法进行跨主机的进程间通信
        #
        # 参数1（domain）：表示协议族，在Linux下只能为AF_LOCAL或者AF_UNIX。（自从Linux 2.6.27后也支持SOCK_NONBLOCK和SOCK_CLOEXEC）
        # 参数2（type）：表示协议，可以是SOCK_STREAM或者SOCK_DGRAM。SOCK_STREAM是基于TCP的，而SOCK_DGRAM是基于UDP的
        # 参数3（protocol）：表示类型，只能为0
        socket_pair = socket.socketpair(
            socket.AF_UNIX, socket.SOCK_STREAM, 0)
    return socket_pair
