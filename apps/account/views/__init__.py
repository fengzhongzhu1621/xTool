import time

from django.http import JsonResponse
from django.middleware import csrf

from .login import LoginTokenView, LoginView, LogoutView
from .user import UserViewSet


def get_user_info(request):

    return JsonResponse(
        {
            "code": 0,
            "data": {"id": request.user.id, "username": request.user.username, "timestamp": time.time()},
            "message": "ok",
        }
    )


def get_csrf_token(request):
    """
    前端获取csrf_token接口
    """
    csrf_token = csrf.get_token(request)
    return JsonResponse({"csrf_token": csrf_token})
