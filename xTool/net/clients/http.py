import logging

import curlify
import requests

from xTool.log import logger


def _gen_header():
    headers = {
        "Content-Type": "application/json",
    }
    return headers


def _http_request(
    method,
    url,
    headers=None,
    data=None,
    verify=False,
    cert=None,
    timeout=None,
    cookies=None,
):
    resp = requests.Response()
    try:
        if method == "GET":
            resp = requests.get(
                url=url,
                headers=headers,
                params=data,
                verify=verify,
                cert=cert,
                timeout=timeout,
                cookies=cookies,
            )
        elif method == "HEAD":
            resp = requests.head(
                url=url,
                headers=headers,
                verify=verify,
                cert=cert,
                timeout=timeout,
                cookies=cookies,
            )
        elif method == "POST":
            resp = requests.post(
                url=url,
                headers=headers,
                json=data,
                verify=verify,
                cert=cert,
                timeout=timeout,
                cookies=cookies,
            )
        elif method == "DELETE":
            resp = requests.delete(
                url=url,
                headers=headers,
                json=data,
                verify=verify,
                cert=cert,
                timeout=timeout,
                cookies=cookies,
            )
        elif method == "PUT":
            resp = requests.put(
                url=url,
                headers=headers,
                json=data,
                verify=verify,
                cert=cert,
                timeout=timeout,
                cookies=cookies,
            )
        else:
            return False, "invalid http method: %s" % method, None
    except requests.exceptions.RequestException as e:
        message = "http error! request: [method=`%s`, url=`%s`, data=`%s`] err=`%s`" % (method, url, data, str(e))
        logger.exception(message)
        return False, message, None
    else:
        # 请求ID
        request_id = resp.headers.get("X-Request-Id")
        # 响应内容打印部分
        content = resp.content if resp.content else ""
        if not logger.isEnabledFor(logging.DEBUG) and len(content) > 200:
            content = content[:200] + b"......"

        message_format = (
            "request: [method=`%s`, url=`%s`, data=`%s`] response: [status_code=`%s`, request_id=`%s`, content=`%s`]"
        )

        if resp.status_code != 200:
            message = message_format % (method, url, str(data), resp.status_code, request_id, content)
            logger.error(message)
            return False, message, None

        logger.info(message_format % (method, url, str(data), resp.status_code, request_id, content))
        return True, "ok", resp.json()
    finally:
        if resp.request is None:
            # 空请求
            resp.request = requests.Request(method, url, headers=headers, data=data, cookies=cookies).prepare()

        if logger.isEnabledFor(logging.DEBUG):
            logger.debug(
                "the request_id: `%s`. curl: `%s`",
                resp.headers.get("X-Request-Id", ""),
                # 将http请求转换curl语句
                curlify.to_curl(resp.request, verify=False),
            )


def http_get(url, data, headers=None, verify=False, cert=None, timeout=None, cookies=None):
    if not headers:
        headers = _gen_header()
    return _http_request(
        method="GET",
        url=url,
        headers=headers,
        data=data,
        verify=verify,
        cert=cert,
        timeout=timeout,
        cookies=cookies,
    )


def http_post(url, data, headers=None, verify=False, cert=None, timeout=None, cookies=None):
    if not headers:
        headers = _gen_header()
    return _http_request(
        method="POST",
        url=url,
        headers=headers,
        data=data,
        verify=verify,
        cert=cert,
        timeout=timeout,
        cookies=cookies,
    )


def http_put(url, data, headers=None, verify=False, cert=None, timeout=None, cookies=None):
    if not headers:
        headers = _gen_header()
    return _http_request(
        method="PUT",
        url=url,
        headers=headers,
        data=data,
        verify=verify,
        cert=cert,
        timeout=timeout,
        cookies=cookies,
    )


def http_delete(url, data, headers=None, verify=False, cert=None, timeout=None, cookies=None):
    if not headers:
        headers = _gen_header()
    return _http_request(
        method="DELETE",
        url=url,
        headers=headers,
        data=data,
        verify=verify,
        cert=cert,
        timeout=timeout,
        cookies=cookies,
    )
