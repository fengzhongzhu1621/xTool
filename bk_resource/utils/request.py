from django.test import RequestFactory

from bk_resource.utils.local import local


def get_request_username(default=""):
    try:
        from core.utils.request_provider import get_local_request

        username = get_local_request().user.username
    except Exception:  # pylint: disable=broad-except
        username = get_local_username()
        if not username:
            username = default
    return username


def get_local_username():
    """从local对象中获取用户信息（celery）"""
    return getattr(local, "username", None)


def set_local_username(username):
    local.username = username


def get_moke_request(**kwargs):
    return RequestFactory().request(**kwargs)
