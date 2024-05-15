import uuid
from contextlib import contextmanager

from werkzeug.local import Local, release_local

__all__ = [
    "request_local",
    "inject_request_id",
    "request_local_injection",
    "release_request_local",
]

# 定义线程变量
request_local = Local()


def inject_request_id(local, http_request):
    """
    将request的对应id注入到local对象中，优先采用http_request中注入的request_id，否则生成一个新的id
    :param local: werkzeug.local对象
    :param http_request: request对象
    :return: None
    """
    request_meta = getattr(http_request, "META", {})
    x_request_id = request_meta.get("HTTP_X_REQUEST_ID") if isinstance(request_meta, dict) else None
    local.request_id = x_request_id or str(uuid.uuid4())


@contextmanager
def _with_request_local(context: dict):
    """从线程变量中去掉指定的值，处理完毕后，重新加回到线程变量中 ."""
    local_vars = {}
    for k in context.keys():
        if hasattr(request_local, k):
            local_vars[k] = getattr(request_local, k)
            delattr(request_local, k)

    try:
        yield request_local
    finally:
        for k in context.keys():
            if hasattr(request_local, k):
                delattr(request_local, k)
        for k, v in list(local_vars.items()):
            setattr(request_local, k, v)


@contextmanager
def request_local_injection(context: dict):
    with _with_request_local(context) as local:
        for k, v in context.items():
            setattr(local, k, v)
        yield


def release_request_local():
    release_local(request_local)
