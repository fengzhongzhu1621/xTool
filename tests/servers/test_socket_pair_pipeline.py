# -*- coding: utf-8 -*-

import pytest
from xTool.servers.socket_pair_pipeline import SocketPairPipeline


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
        with pytest.raises(ConnectionResetError):
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
