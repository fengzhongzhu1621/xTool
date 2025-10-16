import abc
import json
from datetime import datetime

from bk_resource.settings import bk_resource_settings
from bk_resource.utils.logger import logger


class BaseRequestLogHandler:
    def __init__(
        self,
        resource_name: str,
        start_time: datetime,
        end_time: datetime,
        request_data: any,
        response_data: any,
    ):
        self.resource_name = resource_name
        self.start_time = start_time
        self.end_time = end_time
        self.request_data = self.parse_json(request_data)
        self.response_data = self.parse_json(response_data)
        if bk_resource_settings.REQUEST_LOG_SPLIT_LENGTH:
            log_length = len(self.response_data)
            self.response_data = self.response_data[: bk_resource_settings.REQUEST_LOG_SPLIT_LENGTH] + (
                "." * 6 if log_length > bk_resource_settings.REQUEST_LOG_SPLIT_LENGTH else ""
            )

    @abc.abstractmethod
    def record(self): ...

    @classmethod
    def parse_json(cls, data: dict) -> str:
        try:
            return json.dumps(data, ensure_ascii=False)
        except Exception:
            return str(data)


class RequestLogHandler(BaseRequestLogHandler):
    def record(self):
        msg = (
            "[ResourceRequestLog]\n"
            "AppCode => %s\n"
            "Username => %s\n"
            "Resource => %s\n"
            "StartTime => %s\n"
            "EndTime => %s\n"
            "RequestData => %s\n"
            "ResponseData => %s"
        )
        logger.info(
            msg,
            self.get_app_code(),
            self.get_username(),
            self.resource_name,
            self.start_time,
            self.end_time,
            self.request_data,
            self.response_data,
        )

    @classmethod
    def get_username(cls) -> str:
        """获取请求用户名"""
        from core.utils.request_provider import get_local_request

        try:
            return get_local_request().user.username
        except (IndexError, AttributeError):
            return ""

    @classmethod
    def get_app_code(cls) -> str:
        """获取AppCode"""
        from core.utils.request_provider import get_local_request

        try:
            app = get_local_request().app
            return f"{app.bk_app_code}{'' if app.verified else '(unverified)'}"
        except (IndexError, AttributeError):
            return ""
