from django.urls import re_path

from apps.account import views

urlpatterns = [
    re_path(r"^get_user_info/$", views.get_user_info, name="get_user_info"),
    re_path(r"^get_csrf_token/$", views.get_csrf_token, name="get_csrf_token"),
]
