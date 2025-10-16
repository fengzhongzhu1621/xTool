from django.contrib.auth.models import Group, User
from rest_framework import generics, permissions, viewsets

from apps.quickstart.serializers import (
    GroupSerializer,
    UserSerializer,
    UserSerializer2,
)


class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """

    queryset = User.objects.all().order_by("-date_joined")
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]


class GroupViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """

    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    permission_classes = [permissions.IsAuthenticated]


class UserList(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer2


class UserDetail(generics.RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer2
