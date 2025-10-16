from bk_resource import resource
from bk_resource.viewsets import ResourceRoute, ResourceViewSet

__all__ = ["UserViewSet"]


class UserViewSet(ResourceViewSet):
    resource_routes = [
        ResourceRoute("GET", resource.account.retrieve_user, pk_field="id"),
    ]
