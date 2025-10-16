import socket

from xTool.misc import OS_IS_WINDOWS
from xTool.net.ip import is_ipv4, is_ipv6

DEFAULT_BACKLOG = 1500


def new_socket(ip: str, stream: bool = True) -> socket.socket:
    sock = None
    if is_ipv4(ip):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM if stream else socket.SOCK_DGRAM)
    elif is_ipv6(ip):
        sock = socket.socket(socket.AF_INET6, socket.SOCK_STREAM if stream else socket.SOCK_DGRAM)
    return sock


def new_tcp_server_socket(ip: str, port: int, backlog=100, reuse_port=False):
    sock = new_socket(ip, stream=True)
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
        socket_pair = socket.socketpair(socket.AF_UNIX, socket.SOCK_STREAM, 0)
    return socket_pair
