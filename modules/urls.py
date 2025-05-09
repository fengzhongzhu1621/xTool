from django.urls import include, path

from bk_resource.routers import ResourceRouter

base_router = ResourceRouter()

api_v1_urlpatterns = [
    path("", include(base_router.urls)),
]

urlpatterns = (path("api/v1/", include(api_v1_urlpatterns)),)
