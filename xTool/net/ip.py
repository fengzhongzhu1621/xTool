import ipaddress
import socket
import struct

import netifaces

from xTool.misc import tob


def join_address(host: str, port: int) -> str:
    if ":" in host:
        # IPV6：带有端口号的IPV6地址字符串形式，地址部分应用"[]"括起来，在后面跟着":"带上端口号
        return "[{}]:{}".format(host, port)
    else:
        # IPV4
        return "{}:{}".format(host, port)


def get_local_host_ip(ifname=b"eth1", ip: str = None, port: int = None) -> str:
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
    if platform.system() == "Linux":
        import fcntl
        import struct

        ifname = tob(ifname)
        sock = None
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            o_ip = socket.inet_ntoa(fcntl.ioctl(sock.fileno(), 0x8915, struct.pack("256s", ifname[:15]))[20:24])
        finally:
            if sock:
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
        ip_address = net_address[netifaces.AF_INET][0]["addr"]
    elif netifaces.AF_INET6 in net_address:
        ip_address = net_address[netifaces.AF_INET6][0]["addr"]
    else:
        ip_address = ""
    return ip_address


def is_valid_ip(ip_address):
    """是否是合法的ip"""
    try:
        ipaddress.ip_address(ip_address)
        return True
    except ipaddress.AddressValueError:
        return False
    except Exception:
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
    except OSError:
        return False
    return True


def is_ipv6(ip: str) -> bool:
    """判断IP是否为ipv6, 比使用ipaddress性能更高 ."""
    try:
        # 将点分文本的IP地址转换为二进制网络字节序”的IP地址
        socket.inet_pton(socket.AF_INET6, ip)
    except OSError:
        return False
    return True


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
    return socket.inet_ntoa(struct.pack("!L", ip_num))


def ipv6_to_long(ipv6):
    hi, lo = struct.unpack("!QQ", socket.inet_pton(socket.AF_INET6, ipv6))
    return (hi << 64) | lo


def long_to_ipv6(ip_num):
    return socket.inet_ntop(socket.AF_INET6, struct.pack("!QQ", ip_num >> 64, ip_num & 0xFFFFFFFFFFFFFFFF))


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
