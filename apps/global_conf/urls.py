# -*- coding: utf-8 -*-
from bk_resource.routers import ResourceRouter
from django.urls import include, path

from apps.global_conf.views import query_token as query_token_views

router = ResourceRouter()
router.register_module(query_token_views)

urlpatterns = [
    path("", include(router.urls)),
]
