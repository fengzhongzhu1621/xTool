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


class DisableCSRFCheckMiddleware:
    """本地开发，去掉 django rest framework 强制的 csrf 检查"""

    def __init__(self, get_response=None):
        self.get_response = get_response

    def __call__(self, request):
        setattr(request, "_dont_enforce_csrf_checks", True)

        response = self.get_response(request)
        return response
