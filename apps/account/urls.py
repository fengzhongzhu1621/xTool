from django.urls import include, path, re_path

from apps.account import views
from bk_resource.routers import ResourceRouter

router = ResourceRouter()
router.register_module(views)

urlpatterns = [
    path("", include(router.urls)),
    re_path(r"^get_user_info/$", views.get_user_info, name="get_user_info"),
    re_path(r"^get_csrf_token/$", views.get_csrf_token, name="get_csrf_token"),
]
