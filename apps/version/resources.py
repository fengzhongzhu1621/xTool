import abc
from typing import Dict

import orjson as json
from django.utils.translation import gettext_lazy as _lazy
from version_log import config, views
from version_log.models import VersionLogVisited

from apps.version.serializers import VersionLogDetailRequestSerializer
from bk_resource import Resource
from core.utils.request_provider import get_local_request


class VersionBaseResource(Resource, abc.ABC):
    tags = [_lazy("版本日志")]


class VersionLogsListResource(VersionBaseResource):
    name = _lazy("获取版本日志列表")

    def perform_request(self, validated_request_data: Dict) -> Dict:
        # 从本地文件获取版本日志列表
        request = get_local_request()
        response = views.version_logs_list(request)
        logs_list_content: Dict = json.loads(response.content)
        version_logs = []
        for version_info in logs_list_content.get("data", []):
            version_logs.append({"version": version_info[0], "release_at": version_info[1]})

        # 查询当前用户是否看过最新版本日志，判断用户是否访问过最新版本日志，同时更新数据库记录
        response = views.has_user_read_latest(request)
        show_version_result = json.loads(response.content).get("data", {}).get("has_read_latest")
        if not show_version_result:
            username = request.user.username
            # 更新用户访问版本记录
            VersionLogVisited.objects.update_visit_version(username, config.LATEST_VERSION)

        last_version = version_logs[0]["version"] if version_logs else ""
        data = {
            "show_version": not show_version_result,
            "version_logs": version_logs,
            "last_version": last_version,
        }

        return data


class VersionLogDetailResource(VersionBaseResource):
    name = _lazy("获取版本日志详情")
    RequestSerializer = VersionLogDetailRequestSerializer

    def perform_request(self, validated_request_data):
        request = get_local_request()
        content = json.loads(views.get_version_log_detail(request).content).get("data")
        data = {"content": content}
        return data
