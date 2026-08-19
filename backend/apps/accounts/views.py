import logging

from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, generics, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from apps.core.email_service import send_login_success_email

from apps.accounts.models import RefreshTokenAudit, User
from apps.accounts.serializers import (
    ChangePasswordSerializer,
    LoginSerializer,
    ProfileSerializer,
    RegisterSerializer,
    UserAdminUpdateSerializer,
    UserSerializer,
)
from apps.core.permissions import IsAdmin, IsSelfOrAdmin
from apps.core.responses import error_response, success_response

logger = logging.getLogger("apps")


def _client_ip(request):
    xff = request.META.get("HTTP_X_FORWARDED_FOR")
    return xff.split(",")[0].strip() if xff else request.META.get("REMOTE_ADDR")


class RegisterView(generics.CreateAPIView):
    """POST /api/auth/register/ — public signup, mirrors the Next.js form 1:1."""

    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]
    throttle_scope = "auth"

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return success_response(
            data={"user_id": user.id},
            message=(
                "Registration submitted successfully. Your account is awaiting "
                "Admin approval before you can log in."
            ),
            status=status.HTTP_201_CREATED,
        )


class LoginView(TokenObtainPairView):
    """POST /api/auth/login/ — accepts {identifier, password}."""

    serializer_class = LoginSerializer
    permission_classes = [permissions.AllowAny]
    throttle_scope = "auth"

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        try:
            serializer.is_valid(raise_exception=True)

        except Exception:
            RefreshTokenAudit.objects.create(
                action=RefreshTokenAudit.Action.FAILED_LOGIN,
                ip_address=_client_ip(request),
                user_agent=request.META.get("HTTP_USER_AGENT", "")[:255],
            )
            raise

        data = serializer.validated_data
        user = data["user"]

        RefreshTokenAudit.objects.create(
            user_id=data["user"]["id"],
            action=RefreshTokenAudit.Action.LOGIN,
            ip_address=_client_ip(request),
            user_agent=request.META.get("HTTP_USER_AGENT", "")[:255],
        )

        send_login_success_email(User.objects.get(id=data["user"]["id"]))

        return success_response(
            data=data,
            message="Login successful.",
        )


class LogoutView(APIView):
    """POST /api/auth/logout/ — blacklists the provided refresh token."""

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        refresh_token = request.data.get("refresh")
        if not refresh_token:
            return error_response("Refresh token is required.", status=400)
        try:
            token = RefreshToken(refresh_token)
            token.blacklist()
        except TokenError:
            return error_response("Invalid or already-expired refresh token.", status=400)

        RefreshTokenAudit.objects.create(
            user=request.user,
            action=RefreshTokenAudit.Action.LOGOUT,
            ip_address=_client_ip(request),
            user_agent=request.META.get("HTTP_USER_AGENT", "")[:255],
        )
        return success_response(message="Logged out successfully.")


class CustomTokenRefreshView(TokenRefreshView):
    throttle_scope = "auth"

    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        if response.status_code == 200:
            return success_response(data=response.data, message="Token refreshed.")
        return response


class ProfileView(generics.RetrieveUpdateAPIView):
    """GET/PATCH /api/profile/me/ — the logged-in user's own profile."""

    serializer_class = ProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user

    def retrieve(self, request, *args, **kwargs):
        serializer = self.get_serializer(self.get_object())
        return success_response(data=serializer.data)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", True)
        serializer = self.get_serializer(self.get_object(), data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return success_response(data=serializer.data, message="Profile updated successfully.")


class ChangePasswordView(APIView):
    """POST /api/profile/change-password/"""

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        user = request.user
        user.set_password(serializer.validated_data["new_password"])
        user.save(update_fields=["password", "last_updated"])
        return success_response(message="Password changed successfully. Please log in again.")


class UserViewSet(viewsets.ModelViewSet):
    """
    Full CRUD for user management (Admin-only), including approve/reject
    workflow actions for the 'Pending Registrations' dashboard widget.
    """

    queryset = User.objects.all()
    permission_classes = [IsAdmin]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ["role", "account_status", "is_active"]
    search_fields = ["full_name", "username", "email", "employee_id"]
    ordering_fields = ["registration_date", "last_updated", "full_name"]
    ordering = ["-registration_date"]

    def get_serializer_class(self):
        if self.action in ("update", "partial_update"):
            return UserAdminUpdateSerializer
        return UserSerializer

    def get_permissions(self):
        if self.action == "retrieve":
            return [IsSelfOrAdmin()]
        return super().get_permissions()

    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)
        return response

    @action(detail=False, methods=["get"], permission_classes=[IsAdmin])
    def pending(self, request):
        """GET /api/users/pending/ — for the 'Pending Registrations' widget."""
        qs = self.filter_queryset(
            self.get_queryset().filter(account_status=User.AccountStatus.PENDING)
        )
        page = self.paginate_queryset(qs)
        serializer = UserSerializer(page or qs, many=True)
        if page is not None:
            return self.get_paginated_response(serializer.data)
        return success_response(data=serializer.data)

    @action(detail=True, methods=["post"], permission_classes=[IsAdmin])
    def approve(self, request, pk=None):
        user = self.get_object()
        user.account_status = User.AccountStatus.APPROVED
        user.is_active = True
        user.approved_by = request.user
        user.approved_at = timezone.now()
        user.rejection_reason = None
        user.save()
        return success_response(data=UserSerializer(user).data, message="User approved successfully.")

    @action(detail=True, methods=["post"], permission_classes=[IsAdmin])
    def reject(self, request, pk=None):
        reason = request.data.get("reason", "Not specified")
        user = self.get_object()
        user.account_status = User.AccountStatus.REJECTED
        user.is_active = False
        user.rejection_reason = reason
        user.save()
        return success_response(data=UserSerializer(user).data, message="User rejected.")

    @action(detail=True, methods=["post"], permission_classes=[IsAdmin])
    def suspend(self, request, pk=None):
        user = self.get_object()
        user.account_status = User.AccountStatus.SUSPENDED
        user.is_active = False
        user.save()
        return success_response(data=UserSerializer(user).data, message="User suspended.")

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.id == request.user.id:
            return error_response("You cannot delete your own account.", status=400)
        self.perform_destroy(instance)
        return success_response(message="User deleted successfully.")
