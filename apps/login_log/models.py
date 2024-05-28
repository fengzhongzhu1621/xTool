import user_agents
from django.db import models
from django.utils.translation import gettext_lazy as _lazy

from apps.component.constants import LoginType
from core.constants import LEN_NORMAL, LEN_SHORT, LEN_LONG
from core.ip import get_ip_analysis, get_request_ip
from core.models import SoftDeleteModel, SoftDeleteModelManager
from core.request import get_browser, get_os


class LoginLogManager(SoftDeleteModelManager):
    def create_analysis_data(self, request):
        """
        保存登录日志
        """
        ip = get_request_ip(request=request)
        analysis_data = get_ip_analysis(ip)
        analysis_data["username"] = request.user.username
        analysis_data["ip"] = ip
        analysis_data["agent"] = str(user_agents.parse(request.META["HTTP_USER_AGENT"]))
        analysis_data["browser"] = get_browser(request)
        analysis_data["os"] = get_os(request)
        analysis_data["creator_id"] = request.user.id
        analysis_data["dept_belong_id"] = getattr(request.user, "dept_id", "")
        self.create(**analysis_data)


class LoginLog(SoftDeleteModel):

    username = models.CharField(max_length=LEN_SHORT, verbose_name=_lazy("登录用户名"), null=True, blank=True)
    ip = models.CharField(max_length=32, verbose_name=_lazy("登录ip"), null=True, blank=True)
    agent = models.TextField(verbose_name=_lazy("agent信息"), null=True, blank=True)
    browser = models.CharField(max_length=LEN_LONG, verbose_name=_lazy("浏览器名"), null=True, blank=True)
    os = models.CharField(
        max_length=LEN_LONG, verbose_name=_lazy("操作系统"), null=True, blank=True, help_text="操作系统"
    )
    continent = models.CharField(max_length=LEN_NORMAL, verbose_name=_lazy("州"), null=True, blank=True)
    country = models.CharField(max_length=LEN_NORMAL, verbose_name=_lazy("国家"), null=True, blank=True)
    province = models.CharField(max_length=LEN_NORMAL, verbose_name=_lazy("省份"), null=True, blank=True)
    city = models.CharField(max_length=LEN_NORMAL, verbose_name=_lazy("城市"), null=True, blank=True)
    district = models.CharField(max_length=LEN_NORMAL, verbose_name=_lazy("县区"), null=True, blank=True)
    isp = models.CharField(max_length=LEN_NORMAL, verbose_name=_lazy("运营商"), null=True, blank=True)
    area_code = models.CharField(max_length=LEN_NORMAL, verbose_name=_lazy("区域代码"), null=True, blank=True)
    country_english = models.CharField(max_length=LEN_NORMAL, verbose_name=_lazy("英文全称"), null=True, blank=True)
    country_code = models.CharField(max_length=LEN_NORMAL, verbose_name=_lazy("简称"), null=True, blank=True)
    longitude = models.CharField(max_length=LEN_NORMAL, verbose_name=_lazy("经度"), null=True, blank=True)
    latitude = models.CharField(max_length=LEN_NORMAL, verbose_name=_lazy("纬度"), null=True, blank=True)
    login_type = models.CharField(
        default=LoginType.NORMAL.value, max_length=LEN_SHORT, choices=LoginType.choices, verbose_name=_lazy("登录类型")
    )

    objects = LoginLogManager()

    class Meta:
        verbose_name = "登录日志"
        verbose_name_plural = verbose_name
