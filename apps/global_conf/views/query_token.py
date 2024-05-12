from bk_resource import resource
from bk_resource.viewsets import ResourceRoute, ResourceViewSet


class TokenViewSet(ResourceViewSet):
    resource_routes = [
        ResourceRoute("POST", resource.global_conf.generate_query_token, endpoint="generate_query_token"),
        ResourceRoute("GET", resource.global_conf.get_query_data, endpoint="get_query_data"),
    ]
