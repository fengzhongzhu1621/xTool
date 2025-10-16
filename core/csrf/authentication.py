from rest_framework.authentication import SessionAuthentication

__all__ = ["CsrfExemptSessionAuthentication"]


class CsrfExemptSessionAuthentication(SessionAuthentication):
    """
    免除csrf认证
    """

    def enforce_csrf(self, request):  # pylint: disable=no-self-use,unused-argument
        """To not perform the csrf check previously happening"""
        return
