from typing import Dict, List, Optional, Union

from rest_framework.viewsets import GenericViewSet

from apps.snippets.models import Snippet
from core.drf_resource import Resource


class SnippetHighlight(Resource, GenericViewSet):
    queryset = Snippet.objects.all()

    def perform_request(self, validated_request_data: Optional[Dict]) -> Union[List, Dict]:
        snippet = self.get_object()
        return snippet.highlighted
