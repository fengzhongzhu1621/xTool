import uuid
from werkzeug.local import Local

request_local = Local()

# todo 需要django中间件支持


def inject_request_id(local, http_request):
    """
    将request的对应id注入到local对象中，优先采用http_request中注入的request_id，否则生成一个新的id
    """
    request_meta = getattr(http_request, "META", {})
    x_request_id = (
        request_meta.get("HTTP_X_REQUEST_ID")
        if isinstance(request_meta, dict)
        else None
    )
    local.request_id = x_request_id or str(uuid.uuid4())


def get_or_create_local_request_id():
    if not hasattr(request_local, "request_id"):
        request_local.request_id = str(uuid.uuid4())
    return request_local.request_id
