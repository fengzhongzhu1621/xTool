# -*- coding: utf-8 -*-

from dataclasses import dataclass
from typing import List, Optional

from rest_framework import viewsets
from rest_framework.serializers import Serializer
from .base import Resource


@dataclass
class ResourceRoute:
    method: str
    resource_class: Resource
    endpoint: str

    def __post_init__(self):
        self.method = self.method.lower()


class ResourceViewSet(viewsets.GenericViewSet):
    resource_routes: List[ResourceRoute] = []

    def __init__(self, *args, **kwargs) -> None:
        self.resource_routers_map = {item.endpoint: item for item in self.resource_routes}
        super.__init__(*args, **kwargs)

    def get_queryset(self):
        return

    def get_serializer_class(self) -> Optional[Serializer]:
        """
        Return the class to use for the serializer.
        Defaults to using `self.serializer_class`.

        You may want to override this if you need to provide different
        serializations depending on the incoming request.

        (Eg. admins get full serialization, others get basic serialization)
        """
        resource_route = self.resource_routers_map.get(self.action)
        if not resource_route:
            return None
        serializer_class = resource_route.RequestSerializer
        return serializer_class
