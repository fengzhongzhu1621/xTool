# -*- coding: utf-8 -*-

from json import JSONDecodeError

import httpx

from xTool.clients import websocket_client


async def async_httpx_request(method, url, *args, **kwargs):
    raw_cookies = kwargs.pop("raw_cookies", None)

    if method == "websocket":
        async with websocket_client.connect(url, *args, **kwargs) as client:
            return client
    else:
        async with httpx.AsyncClient(verify=False, trust_env=False) as session:
            try:
                # 发送http请求
                response = await getattr(session, method.lower())(
                    url, *args, **kwargs
                )
            except NameError:
                raise Exception(response.status_code)

            # 读取响应内容
            response.body = await response.aread()
            response.status = response.status_code
            response.content_type = response.headers.get("content-type")

            # response can be decoded as json after response._content
            # is set by response.aread()
            try:
                response.json = response.json()
            except (JSONDecodeError, UnicodeDecodeError):
                response.json = None

            if raw_cookies:
                response.raw_cookies = {}

                for cookie in response.cookies.jar:
                    response.raw_cookies[cookie.name] = cookie

            return response
