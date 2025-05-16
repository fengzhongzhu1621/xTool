"""apps URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.conf import settings
from django.contrib import admin
from django.urls import include, path
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework_simplejwt.views import (
    TokenRefreshView,
)

from apps import views
from apps.account.views import LoginTokenView, LoginView, LogoutView
from apps.entry import views as EntryViews
from apps.version import views as VersionViews
from bk_resource.routers import ResourceRouter
from core.permissions import SwaggerPermission

info = openapi.Info(
    title="xTool",
    default_version="v1",
    description="A Python learning project",
)
schema_view = get_schema_view(
    info,
    public=True,
    permission_classes=(SwaggerPermission,),
)

base_router = ResourceRouter()
base_router.register_module(VersionViews)
base_router.register_module(EntryViews)

urlpatterns = [
    path("admin/", admin.site.urls),
    path("account/", include("apps.account.urls")),
    # path("pipeline_admin/", include("pipeline.contrib.engine_admin.urls")),
    path("api-auth/", include("rest_framework.urls", namespace="rest_framework")),
    path("swagger/", schema_view.with_ui(cache_timeout=0), name="schema-swagger-ui"),
    path("i18n/", include("django.conf.urls.i18n")),
    path("api_root", views.api_root),
    # path("quickstart/", include("apps.quickstart.urls")),
    # path("snippets/", include("apps.snippets.urls")),
    path("global_conf/", include("apps.global_conf.urls")),
    path("", include(base_router.urls)),
    # 登录
    path("api/login/", LoginView.as_view(), name="token_obtain_pair"),
    path("api/logout/", LogoutView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    # 仅用于开发，上线需关闭
    path("api/token/", LoginTokenView.as_view()),
]

# 加载模块
for _module in settings.DEPLOY_MODULE:
    urlpatterns.append(path("", include(f"{settings.MODULE_PATH}.{_module}.urls")))

if settings.DEBUG and settings.DEBUG_TOOL_BAR:
    import debug_toolbar

    urlpatterns = [
        path("__debug__/", include(debug_toolbar.urls)),
    ] + urlpatterns
