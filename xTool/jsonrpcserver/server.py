#coding: utf-8
import logging
from http.server import BaseHTTPRequestHandler, HTTPServer

from .dispatcher import dispatch


class RequestHandler(BaseHTTPRequestHandler):
    def do_POST(self) -> None:
        """HTTP POST"""
        # Process request
        # 获得请求的body
        request = self.rfile.read(int(str(self.headers["Content-Length"]))).decode()
        # 执行method
        response = dispatch(request)
        # Return response
        # 如果不是通知，则返回结果
        if response.wanted:
            # 设置返回状态码
            self.send_response(response.http_status)
            # 设置json返回头
            self.send_header("Content-type", "application/json")
            self.end_headers()
            # 返回响应
            self.wfile.write(str(response).encode())


def serve(name: str = "", port: int = 5000) -> None:
    """
    A basic way to serve the methods.

    Args:
        name: Server address.
        port: Server port.
    """
    logging.info(" * Listening on port %s", port)
    httpd = HTTPServer((name, port), RequestHandler)
    httpd.serve_forever()
