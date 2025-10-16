from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView

from apps.account.serializers import LoginSerializer, LoginTokenSerializer
from core.response import DetailResponse


class LoginTokenView(TokenObtainPairView):
    """
    登录获取token接口
    """

    serializer_class = LoginTokenSerializer
    permission_classes = []


class LoginView(TokenObtainPairView):
    """
    登录接口
    """

    serializer_class = LoginSerializer
    permission_classes = []


class LogoutView(APIView):
    def post(self, request):
        return DetailResponse(msg="注销成功")
