# -*- coding: utf-8 -*-

import multiprocessing
import pytest
from xTool.servers.pipeline import SocketPairPipeline


def _task(server_connector, message):
    server_connector.close_other_side()
    server_connector.send(message)


def _task_with_queue(queue, message):
    queue.put(message)


class TestSocketPairPipeline:
    def test_read_and_write(self):
        pipeline = SocketPairPipeline()
        client_fileno = pipeline.client_fileno
        server_fileno = pipeline.server_fileno
        assert client_fileno > 0
        assert server_fileno > 0

        message = b"hello world!"

        pipeline.send_to_server(message)
        actual = pipeline.recv_from_client(100)
        assert actual == message

        pipeline.send_to_client(message)
        actual = pipeline.recv_from_server(100)
        assert actual == message

    def test_close(self):
        pipeline = SocketPairPipeline()
        message = b"hello world!"
        pipeline.send_to_server(message)
        pipeline.close_server()
        # with pytest.raises(ConnectionResetError):
        with pytest.raises(BrokenPipeError):
            pipeline.send_to_server(message)
        with pytest.raises(OSError):
            pipeline.send_to_client(message)

    def test_create_connectors(self):
        pipeline = SocketPairPipeline()
        server_connector, client_connector = pipeline.create_connectors()

        message = b"hello world!"

        client_connector.send(message)
        actual = server_connector.recv(100)
        assert actual == message

        server_connector.send(message)
        actual = client_connector.recv(100)
        assert actual == message

    def test_communicate_between_parent_and_children_process(self):
        """测试父子进程之间的通信 ."""
        pipeline = SocketPairPipeline()
        server_connector, client_connector = pipeline.create_connectors()

        message = b"hello world!"

        child = multiprocessing.Process(target=_task, args=(server_connector, message))
        child.start()
        child.join()
        client_connector.close_other_side()
        actual = client_connector.recv(100)
        assert actual == message

    def test_communicate_use_queue(self):
        """测试父子进程之间的通信 ."""
        queue = multiprocessing.Queue()
        message = b"hello world!"

        child = multiprocessing.Process(target=_task_with_queue, args=(queue, message))
        child.start()
        child.join()
        actual = queue.get()
        assert actual == message
