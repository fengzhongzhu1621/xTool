import json

from django.conf import settings
from django.utils.deprecation import MiddlewareMixin

from apps.account.models import OperationLog
from core.models import get_verbose_name
from core.request import (
    get_browser,
    get_or_create_local_request_id,
    get_os,
    get_request_data,
    get_request_ip,
    get_request_path,
)


class ApiLoggingMiddleware(MiddlewareMixin):
    """
    用于记录API访问日志中间件
    """

    def __init__(self, get_response=None):
        super().__init__(get_response)
        self.enable = getattr(settings, "API_LOG_ENABLE", None) or False
        self.methods = getattr(settings, "API_LOG_METHODS", None) or set()
        self.operation_log_id = None

    @classmethod
    def __handle_request(cls, request):
        request.request_ip = get_request_ip(request)
        request.request_data = get_request_data(request)
        request.request_path = get_request_path(request)

    def __handle_response(self, request, response):
        # request_data,request_ip由PermissionInterfaceMiddleware中间件中添加的属性
        body = getattr(request, "request_data", {})
        if isinstance(body, dict) and body.get("password", ""):
            body["password"] = "*" * len(body["password"])
        response_content = response.content
        try:
            if response_content:
                response_content = json.loads(response.content.decode())
        except Exception:
            pass
        info = {
            "request_ip": getattr(request, "request_ip", "unknown"),
            "request_method": request.method,
            "request_path": request.request_path,
            "request_body": body,
            "request_os": get_os(request),
            "request_browser": get_browser(request),
            "request_msg": request.session.get("request_msg"),  # 操作说明
            "response_code": response.status_code,
            "response_content": response_content,
            "request_id": get_or_create_local_request_id(),
        }
        operation_log, _created = OperationLog.objects.update_or_create(defaults=info, id=self.operation_log_id)
        # 记录请求模块
        if not operation_log.request_modular and settings.API_MODEL_MAP.get(request.request_path, None):
            operation_log.request_modular = settings.API_MODEL_MAP[request.request_path]
            operation_log.save()

    def process_view(self, request, view_func, view_args, view_kwargs):
        if hasattr(view_func, "cls") and hasattr(view_func.cls, "queryset"):
            if self.enable:
                if self.methods == "ALL" or request.method in self.methods:
                    log = OperationLog(request_modular=get_verbose_name(view_func.cls.queryset))
                    log.save()
                    self.operation_log_id = log.id

        return

    def process_request(self, request):
        self.__handle_request(request)

    def process_response(self, request, response):
        """
        主要请求处理完之后记录
        :param request:
        :param response:
        :return:
        """
        if self.enable:
            if self.methods == "ALL" or request.method in self.methods:
                self.__handle_response(request, response)
        return response
