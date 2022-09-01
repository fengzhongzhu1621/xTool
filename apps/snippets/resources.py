from typing import Optional, Union, List, Dict

from apps.core.drf_resource import Resource
from apps.snippets.models import Snippet
from rest_framework.viewsets import GenericViewSet


class SnippetHighlight(Resource, GenericViewSet):
    queryset = Snippet.objects.all()

    def perform_request(self, validated_request_data: Optional[Dict]) -> Union[List, Dict]:
        snippet = self.get_object()
        return snippet.highlighted
