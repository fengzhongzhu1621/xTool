from django.urls import include, path

from apps.quickstart import views
from rest_framework import routers

router = routers.DefaultRouter()
router.register(r'users', views.UserViewSet)
router.register(r'groups', views.GroupViewSet)

# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    path('', include(router.urls)),
    path('users2/', views.UserList.as_view()),
    path('users2/<int:pk>/', views.UserDetail.as_view()),
]
