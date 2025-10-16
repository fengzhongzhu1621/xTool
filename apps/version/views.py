from apps.version.resources import VersionLogDetailResource, VersionLogsListResource
from bk_resource.viewsets import ResourceRoute, ResourceViewSet


class VersionViewSet(ResourceViewSet):
    resource_routes = [
        # 获取版本日志列表
        ResourceRoute("GET", VersionLogsListResource, endpoint="version_logs_list"),
        # 获取版本日志详情
        ResourceRoute("GET", VersionLogDetailResource, endpoint="version_log_detail"),
    ]
