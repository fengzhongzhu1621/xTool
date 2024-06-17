import uuid
from typing import Dict

import orjson as json
import user_agents
from django.urls.resolvers import ResolverMatch
from werkzeug.local import Local

request_local = Local()

# todo 需要django中间件支持


def inject_request_id(local, http_request) -> None:
    """
    将request的对应id注入到local对象中，优先采用http_request中注入的request_id，否则生成一个新的id
    """
    request_meta = getattr(http_request, "META", {})
    x_request_id = request_meta.get("HTTP_X_REQUEST_ID") if isinstance(request_meta, dict) else None
    local.request_id = x_request_id or str(uuid.uuid4())


def get_or_create_local_request_id() -> str:
    if not hasattr(request_local, "request_id"):
        request_local.request_id = str(uuid.uuid4())
    return request_local.request_id


def get_browser(request) -> str:
    """
    获取浏览器名
    """
    ua_string = request.META["HTTP_USER_AGENT"]
    user_agent = user_agents.parse(ua_string)
    return user_agent.get_browser()


def get_os(request) -> str:
    """获取操作系统 ."""
    ua_string = request.META["HTTP_USER_AGENT"]
    user_agent = user_agents.parse(ua_string)
    return user_agent.get_os()


def get_request_canonical_path(
    request,
):
    """获取请求路径 ."""
    request_path = getattr(request, "request_canonical_path", None)
    if request_path:
        return request_path
    path: str = request.path
    resolver_match: ResolverMatch = request.resolver_match
    for value in resolver_match.args:
        path = path.replace(f"/{value}", "/{id}")
    for key, value in resolver_match.kwargs.items():
        if key == "pk":
            path = path.replace(f"/{value}", f"/{{id}}")
            continue
        path = path.replace(f"/{value}", f"/{{{key}}}")

    return path


def get_request_data(request) -> Dict:
    """获取请求参数 ."""
    request_data = getattr(request, "request_data", None)
    if request_data:
        return request_data
    data: dict = {**request.GET.dict(), **request.POST.dict()}
    if not data:
        try:
            body = request.body
            if body:
                data = json.loads(body)
        except Exception:
            pass
        if not isinstance(data, dict):
            data = {"data": data}

    return data


def get_request_user(request):
    """
    获取请求user
    """

    from django.contrib.auth.models import AbstractBaseUser, AnonymousUser
    from rest_framework_simplejwt.authentication import JWTAuthentication

    user: AbstractBaseUser = getattr(request, "user", None)
    if user and user.is_authenticated:
        return user
    try:
        user, _token = JWTAuthentication().authenticate(request)
    except Exception:
        pass
    return user or AnonymousUser()


def get_request_path(request, *args, **kwargs):
    """
    获取请求路径
    :param request:
    :param args:
    :param kwargs:
    :return:
    """
    request_path = getattr(request, "request_path", None)
    if request_path:
        return request_path
    values = []
    for arg in args:
        if len(arg) == 0:
            continue
        if isinstance(arg, str):
            values.append(arg)
        elif isinstance(arg, (tuple, set, list)):
            values.extend(arg)
        elif isinstance(arg, dict):
            values.extend(arg.values())
    if len(values) == 0:
        return request.path
    path: str = request.path
    for value in values:
        path = path.replace("/" + value, "/" + "{id}")
    return path


def get_request_ip(request) -> str:
    """获取请求IP ."""
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR", "")
    if x_forwarded_for:
        ip = x_forwarded_for.split(",")[-1].strip()
        return ip
    ip = request.META.get("REMOTE_ADDR", "") or getattr(request, "request_ip", None)

    return ip or "unknown"
