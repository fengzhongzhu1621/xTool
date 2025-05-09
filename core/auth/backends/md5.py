import logging
from typing import Any

from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.hashers import check_password
from django.utils import timezone
from django.utils.translation import gettext as _
from rest_framework.exceptions import ValidationError

from xTool.codec import md5

logger = logging.getLogger(__name__)
UserModel = get_user_model()


class Md5ModelBackend(ModelBackend):

    def authenticate(self, request, username=None, password=None, **kwargs) -> Any:
        msg = "%s 正在使用本地登录 ..." % username
        logger.info(msg)
        # 获得用户名
        if username is None:
            username = kwargs.get(UserModel.USERNAME_FIELD)
        if username is None or password is None:
            return
        # 查询用户是否存在
        try:
            user = UserModel._default_manager.get_by_natural_key(username)
        except UserModel.DoesNotExist:
            # 创建用户并设置密码
            UserModel().set_password(md5(password))
        else:
            # 验证用户密码
            verify_password = check_password(password, user.password)
            if not verify_password:
                password = md5(password)
                verify_password = check_password(password, user.password)
            if verify_password:
                active = self.user_can_authenticate(user)
                if active:
                    # 更新用户的最新登录时间
                    user.last_login = timezone.now()
                    user.save()
                    return user
                else:
                    raise ValidationError(_("当前用户已被禁用，请联系管理员!"))
            # 密码错误
