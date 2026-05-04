"""
Custom JWT authentication using HttpOnly cookies.
Falls back to Authorization header for API tools (Swagger, Postman).
"""

from rest_framework_simplejwt.authentication import JWTAuthentication
from django.conf import settings


class CookieJWTAuthentication(JWTAuthentication):
    """
    Reads JWT access token from HttpOnly cookie first,
    falls back to Authorization header.
    Invalid/expired cookies are silently ignored so AllowAny views still
    work for users with stale cookies.
    """

    def authenticate(self, request):
        raw_token = request.COOKIES.get(
            getattr(settings, "JWT_ACCESS_COOKIE_NAME", "access_token")
        )
        if raw_token is not None:
            try:
                validated_token = self.get_validated_token(raw_token)
                return self.get_user(validated_token), validated_token
            except Exception:
                pass
        return super().authenticate(request)
