# -*- coding: utf-8 -*-

from django.conf import settings
from django.utils.deprecation import MiddlewareMixin


class CSRFExemptMiddleware(MiddlewareMixin):
    def process_request(self, request):
        if settings.DEBUG or any(
            [
                hasattr(request, "path") and any(request.path.startswith(path) for path in settings.CSRF_EXEMPT_PATHS),
            ]
        ):
            setattr(request, "csrf_processing_done", True)
