import logging
import socket
from typing import Iterable, Tuple

OptionsType = Iterable[Tuple[int, int, int]]


def bind_socket(
    address: str,
    port: int,
    family=socket.AF_INET,
    type=socket.SOCK_STREAM,
    options: OptionsType = (),
    reuse_addr: bool = True,
    reuse_port: bool = False,
    proto_name: str = "tcp",
):
    """绑定端口 ."""
    sock = socket.socket(family, type)
    # 设置为非阻塞模式
    sock.setblocking(False)
    # 用于对TCP套接字处于TIME_WAIT状态下的socket，才可以重复绑定使用。
    # server程序总是应该在调用bind()之前设置SO_REUSEADDR套接字选项。对于TCP，先调用close()的一方会进入TIME_WAIT状态
    # 并不是说让两个程序在相同地址（相同的IP 和 端口）上监听，而是说可以让处于time_wait状态的socket可以快速复用
    # 只有针对time-wait链接(linux系统time-wait连接持续时间为1min)，确保server重启成功的这一个作用
    # 只要有socket处于listen状态， 就不能在同样的地址和端口上listen， 0.0.0.0 与其他所有地址冲突
    # SO_REUSEADDR 允许在同一端口上启动同一服务器的多个实例，只要每个实例捆绑一个不同的本地IP地址即可。对于TCP，我们根本不可能启动捆绑相同I地址和相同端口号的多个服务器。
    # SO_REUSEADDR 允许单个进程捆绑同一端口到多个套接口上，只要每个捆绑指定不同的本地IP地址即可。这一般不用于TCP服务器。
    # SO_REUSEADDR 允许完全重复的捆绑：当一个IP地址和端口绑定到某个套接口上时，还允许此IP地址和端口捆绑到另一个套接口上。一般来说，这个特仅在支持多播的系统上才有，而且只对UDP套接口而言（TCP不支持多播）。
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, int(reuse_addr))
    # linux kernel 3.9 引入了最新的SO_REUSEPORT选项，使得多进程或者多线程创建多个绑定同一个ip:port的监听socket，
    # 提高服务器的接收链接的并发能力,程序的扩展性更好；此时需要设置SO_REUSEPORT（注意所有进程都要设置才生效）
    # 每一个进程有一个独立的监听socket，并且bind相同的ip:port，独立的listen()和accept()；提高接收连接的能力。（例如nginx多进程同时监听同一个ip:port）
    # 内核层面实现负载均衡，保证每个进程或者线程接收均衡的连接数。
    if hasattr(socket, "SO_REUSEPORT"):
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, int(reuse_port))
    else:
        logging.warning("SO_REUSEPORT is not implemented by underlying library.")

    # level: 支持SOL_SOCKET、IPPROTO_TCP、IPPROTO_IP和IPPROTO_IPV6
    for level, option, value in options:
        sock.setsockopt(level, option, value)

    sock.bind((address, port))
    # 返回套接字自己的地址，返回值通常是一个tuple(ipaddr, port)
    sock_addr = sock.getsockname()[:2]

    if sock.family == socket.AF_INET6:
        logging.info("Listening %s://[%s]:%s", proto_name, *sock_addr)
    else:
        logging.info("Listening %s://%s:%s", proto_name, *sock_addr)

    return sock
