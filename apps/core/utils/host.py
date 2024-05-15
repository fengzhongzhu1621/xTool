__all__ = [
    "get_app_host_by_request",
    "resolve_login_url",
]


def get_app_host_by_request(request):
    """通过request对象拼接 app_host 访问地址"""
    return f'{request.META["wsgi.url_scheme"]}://{request.META["HTTP_HOST"]}{request.META["SCRIPT_NAME"]}'


def resolve_login_url(url, request=None, fix_scheme=None):
    """根据网络协议解析url"""
    if url.startswith("http://") or url.startswith("https://"):
        return url
    if fix_scheme:
        return f"{fix_scheme}://{url}"
    scheme = getattr(request, "scheme", "http")
    return f"{scheme}://{url}"
