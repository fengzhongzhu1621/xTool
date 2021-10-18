# -*- coding: utf-8 -*-

from abc import ABCMeta, abstractmethod
from xTool.utils.net import new_socketpair


class IPipelineConnector(metaclass=ABCMeta):
    @abstractmethod
    def close_other_side(self):
        raise NotImplementedError


class BaseSocketPairPipelineConnector(IPipelineConnector):
    __slots__ = ["_socket"]

    def __init__(self, one_of_socket_pair):
        self._socket = one_of_socket_pair

    @property
    def fileno(self):
        return self._socket.fileno()

    def send(self, data):
        self._socket.sendall(data)

    def recv(self, length):
        return self._socket.recv(length)

    def shutdown(self, how: int) -> None:
        self._socket.shutdown(how)

    def close(self):
        self._socket.close()

    @abstractmethod
    def close_other_side(self):
        raise NotImplementedError


class SocketPairPipelineServerConnector(BaseSocketPairPipelineConnector):
    def __init__(self, socket_pair):
        self.server_sock, self.client_sock = socket_pair
        super().__init__(self.server_sock)

    def close_other_side(self):
        self.client_sock.close()


class SocketPairPipelineClientConnector(BaseSocketPairPipelineConnector):
    def __init__(self, socket_pair):
        self.server_sock, self.client_sock = socket_pair
        super().__init__(self.client_sock)

    def close_other_side(self):
        self.server_sock.close()


class SocketPairPipeline:
    def __init__(self):
        self.socket_pair = new_socketpair()
        self.server_sock, self.client_sock = self.socket_pair

    @property
    def server_fileno(self):
        return self.server_sock.fileno()

    @property
    def client_fileno(self):
        return self.client_sock.fileno()

    def create_connectors(self):
        return (
            SocketPairPipelineServerConnector(self.socket_pair),
            SocketPairPipelineClientConnector(self.socket_pair)
        )

    def send_to_client(self, data):
        self.server_sock.sendall(data)

    def recv_from_client(self, length):
        return self.server_sock.recv(length)

    def send_to_server(self, data):
        self.client_sock.sendall(data)

    def recv_from_server(self, length):
        return self.client_sock.recv(length)

    def close_server(self):
        self.server_sock.close()

    def close_client(self):
        self.client_sock.close()

    def shutdown_client(self, how: int) -> None:
        """关闭客户端socket

        :param how:  socket.SHUT_RD: int; socket.SHUT_RDWR: int
        :return:
        """
        self.client_sock.shutdown(how)

    def shutdown_server(self, how: int) -> None:
        """关闭服务端socket

        :param how:  socket.SHUT_RD: int; socket.SHUT_RDWR: int
        :return:
        """
        self.server_sock.shutdown(how)
