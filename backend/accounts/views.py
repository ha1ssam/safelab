"""
Accounts app — Views.
JWT login/logout/register flows backed by HttpOnly cookies.
"""

from django.conf import settings
from rest_framework import status, generics, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from drf_spectacular.utils import extend_schema

from .models import User
from .serializers import UserSerializer, RegisterSerializer, LoginSerializer


def _set_jwt_cookies(response: Response, refresh: RefreshToken) -> None:
    """Attach access + refresh JWT cookies to the response."""
    access_lifetime = settings.SIMPLE_JWT["ACCESS_TOKEN_LIFETIME"]
    refresh_lifetime = settings.SIMPLE_JWT["REFRESH_TOKEN_LIFETIME"]

    response.set_cookie(
        key=settings.JWT_ACCESS_COOKIE_NAME,
        value=str(refresh.access_token),
        max_age=int(access_lifetime.total_seconds()),
        httponly=settings.JWT_COOKIE_HTTPONLY,
        secure=settings.JWT_COOKIE_SECURE,
        samesite=settings.JWT_COOKIE_SAMESITE,
    )
    response.set_cookie(
        key=settings.JWT_REFRESH_COOKIE_NAME,
        value=str(refresh),
        max_age=int(refresh_lifetime.total_seconds()),
        httponly=settings.JWT_COOKIE_HTTPONLY,
        secure=settings.JWT_COOKIE_SECURE,
        samesite=settings.JWT_COOKIE_SAMESITE,
    )


@extend_schema(tags=["Auth"])
class RegisterView(generics.CreateAPIView):
    """Public endpoint to create a new analyst account."""

    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        refresh = RefreshToken.for_user(user)
        response = Response(
            {"user": UserSerializer(user).data},
            status=status.HTTP_201_CREATED,
        )
        _set_jwt_cookies(response, refresh)
        return response


@extend_schema(tags=["Auth"])
class LoginView(APIView):
    """Authenticate by email/password — sets JWT cookies on success."""

    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]

        refresh = RefreshToken.for_user(user)
        response = Response({"user": UserSerializer(user).data})
        _set_jwt_cookies(response, refresh)
        return response


@extend_schema(tags=["Auth"])
class LogoutView(APIView):
    """Clear JWT cookies and blacklist the refresh token if present."""

    permission_classes = [permissions.AllowAny]

    def post(self, request):
        refresh_cookie = request.COOKIES.get(settings.JWT_REFRESH_COOKIE_NAME)
        if refresh_cookie:
            try:
                token = RefreshToken(refresh_cookie)
                token.blacklist()
            except Exception:
                pass

        response = Response({"detail": "Sessão encerrada."})
        response.delete_cookie(settings.JWT_ACCESS_COOKIE_NAME)
        response.delete_cookie(settings.JWT_REFRESH_COOKIE_NAME)
        return response


@extend_schema(tags=["Auth"])
class MeView(generics.RetrieveUpdateAPIView):
    """Return / update the authenticated user's profile."""

    serializer_class = UserSerializer

    def get_object(self):
        return self.request.user
