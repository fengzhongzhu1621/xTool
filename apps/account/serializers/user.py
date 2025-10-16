from apps.account.models import Users
from core.drf.serializers import ModelSerializer

__all__ = ["RetrieveUserRequestSerializer"]


class RetrieveUserRequestSerializer(ModelSerializer):

    class Meta:
        model = Users
        fields = "__all__"
