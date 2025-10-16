from django.urls import include, path
from rest_framework import routers

from apps.quickstart import views

user_list = views.UserViewSet.as_view({"get": "list"})
user_detail = views.UserViewSet.as_view({"get": "retrieve"})

# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    path("users2/", views.UserList.as_view()),
    path("users2/<int:pk>/", views.UserDetail.as_view()),
    path("users3/", user_list, name="user-list"),
    path("users3/<int:pk>/", user_detail, name="user-detail"),
]

router = routers.DefaultRouter()
router.register(r"users", views.UserViewSet, basename="users")
router.register(r"groups", views.GroupViewSet)
urlpatterns += [
    path("", include(router.urls)),
]
