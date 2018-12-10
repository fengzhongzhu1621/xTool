from unittest.mock import patch

from xTool.jsonrpcserver.server import serve


@patch("xTool.jsonrpcserver.server.HTTPServer")
def test_serve(*_):
    serve()
