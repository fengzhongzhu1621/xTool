from django.urls import include, path

from apps.global_conf.views import query_token as query_token_viewset_module
from bk_resource.routers import ResourceRouter

router = ResourceRouter()
router.register_module(query_token_viewset_module)

urlpatterns = [
    path("", include(router.urls)),
]
