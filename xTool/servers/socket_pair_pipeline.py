# -*- coding: utf-8 -*-

import socket
from xTool.misc import OS_IS_WINDOWS


class SocketPairPipeline:
    def __init__(self):
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
        self.left_sock, self.right_sock = socket_pair

    @property
    def left_fileno(self):
        return self.left_sock.fileno()

    @property
    def right_fileno(self):
        return self.right_sock.fileno()

    def send_into_left(self, data):
        self.left_sock.sendall(data)

    def recv_from_left(self, length):
        return self.left_sock.recv(length)

    def send_into_right(self, data):
        self.right_sock.sendall(data)

    def recv_from_right(self, length):
        return self.right_sock.recv(length)

    def close_left(self):
        self.right_sock.close()

    def close_right(self):
        self.right_sock.close()
