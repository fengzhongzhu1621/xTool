from bk_resource import resource
from bk_resource.viewsets import ResourceRoute, ResourceViewSet


class VersionViewSet(ResourceViewSet):
    resource_routes = [
        ResourceRoute("GET", resource.version.version_logs_list, endpoint="version_logs_list"),
        ResourceRoute("GET", resource.version.version_log_detail, endpoint="version_log_detail"),
    ]
