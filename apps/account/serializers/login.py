from datetime import datetime, timedelta

from captcha.views import CaptchaStore
from django.conf import settings
from django.utils.translation import gettext_lazy as _lazy
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from apps.account.models import OperationLog, Users
from apps.global_conf.models import GlobalConfig
from bk_resource.exceptions import ValidateException


class LoginTokenSerializer(TokenObtainPairSerializer):
    """
    登录的序列化器:
    """

    class Meta:
        model = Users
        fields = "__all__"
        read_only_fields = ["id"]

    default_error_messages = {"no_active_account": _lazy("账号/密码不正确")}

    def validate(self, attrs):
        if not getattr(settings, "LOGIN_NO_CAPTCHA_AUTH", False):
            return {"code": 4000, "msg": "该接口暂未开通!", "data": None}
        data = super().validate(attrs)
        data["name"] = self.user.name
        data["userId"] = self.user.id

        return {"code": 2000, "msg": "请求成功", "data": data}


class LoginSerializer(TokenObtainPairSerializer):
    """
    登录的序列化器:
    重写djangorestframework-simplejwt的序列化器
    """

    captcha = serializers.CharField(max_length=6, required=False, allow_null=True, allow_blank=True)

    class Meta:
        model = Users
        fields = "__all__"
        read_only_fields = ["id"]

    default_error_messages = {"no_active_account": _lazy("账号/密码错误")}

    def validate(self, attrs):
        captcha = self.initial_data.get("captcha", None)
        if GlobalConfig.objects.get_value("base.captcha_state", True):
            if captcha is None:
                raise ValidateException("验证码不能为空")
            self.image_code = CaptchaStore.objects.filter(id=self.initial_data["captchaKey"]).first()
            five_minute_ago = datetime.now() - timedelta(hours=0, minutes=5, seconds=0)
            if self.image_code and five_minute_ago > self.image_code.expiration:
                self.image_code and self.image_code.delete()
                raise ValidateException("验证码过期")
            else:
                if self.image_code and (self.image_code.response == captcha or self.image_code.challenge == captcha):
                    self.image_code and self.image_code.delete()
                else:
                    self.image_code and self.image_code.delete()
                    raise ValidateException("图片验证码错误")

        user = Users.objects.get(username=attrs["username"])
        if not user.is_active:
            raise ValidateException("账号被锁定")

        data = super().validate(attrs)
        data["name"] = self.user.name
        data["userId"] = self.user.id
        data["avatar"] = self.user.avatar
        data["user_type"] = self.user.user_type
        dept = getattr(self.user, "dept", None)
        if dept:
            data["dept_info"] = {
                "dept_id": dept.id,
                "dept_name": dept.name,
            }
        role = getattr(self.user, "role", None)
        if role:
            data["role_info"] = role.values("id", "name", "key")
        request = self.context.get("request")
        request.user = self.user
        # 记录登录日志
        OperationLog.objeccts.save_login_log(request=request)
        return {"code": 2000, "msg": "请求成功", "data": data}
