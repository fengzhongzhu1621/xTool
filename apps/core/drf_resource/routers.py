from rest_framework.routers import DefaultRouter


class ResourceRouter(DefaultRouter):
    def register(self, prefix, viewset, basename=None):
        resource_routes = viewset.resource_routes
        for resource_route in resource_routes:
            method = resource_route.method
            method = resource_route.method
            method = resource_route.method
        if basename is None:
            basename = self.get_default_basename(viewset)
        self.registry.append((prefix, viewset, basename))

        # invalidate the urls cache
        if hasattr(self, '_urls'):
            del self._urls
