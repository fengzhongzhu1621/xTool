from bk_resource import resource
from bk_resource.viewsets import ResourceRoute, ResourceViewSet


class ViewSet(ResourceViewSet):
    resource_routes = [
        ResourceRoute("GET", resource.entry.home),
        ResourceRoute("GET", resource.entry.logout, endpoint="logout"),
    ]


class HealthzViewSet(ResourceViewSet):
    def get_authenticators(self):
        return []

    def get_permissions(self):
        return []

    resource_routes = [
        ResourceRoute("GET", resource.entry.healthz, endpoint="healthz"),
        ResourceRoute("GET", resource.entry.ping, endpoint="ping"),
    ]
