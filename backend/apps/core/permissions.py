"""
Role-Based Access Control (RBAC) permission classes shared across every app.

Roles (from apps.accounts.models.User.Role):
    ADMIN     - full control: user management, settings, backup/restore, CRUD everywhere
    OPERATOR  - can manage stations/sensors and acknowledge alerts, but cannot manage
                users, system settings, or backups
    VIEWER    - read-only access everywhere
"""

from rest_framework.permissions import SAFE_METHODS, BasePermission


def _role(request):
    user = request.user
    return getattr(user, "role", None) if user and user.is_authenticated else None


class IsAdmin(BasePermission):
    """Allows access only to Admin role (or Django superusers)."""

    message = "This action requires Administrator privileges."

    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return False
        return user.is_superuser or _role(request) == "ADMIN"


class IsOperatorOrAdmin(BasePermission):
    """Allows Operators and Admins to write; anyone authenticated can read."""

    message = "This action requires Operator or Administrator privileges."

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        if request.method in SAFE_METHODS:
            return True
        return request.user.is_superuser or _role(request) in ("ADMIN", "OPERATOR")


class IsViewerOrAbove(BasePermission):
    """Any authenticated, approved user (Admin, Operator, or Viewer) can read."""

    message = "You must be an approved, authenticated user to access this resource."

    def has_permission(self, request, view):
        user = request.user
        return bool(
            user
            and user.is_authenticated
            and (user.is_superuser or getattr(user, "account_status", None) == "APPROVED")
        )


class ReadOnlyForViewer(BasePermission):
    """
    Generic object-level helper: Viewers get SAFE_METHODS only, Operators and
    Admins get full CRUD. Use alongside IsViewerOrAbove.
    """

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        return _role(request) in ("ADMIN", "OPERATOR") or request.user.is_superuser


class IsSelfOrAdmin(BasePermission):
    """Object-level permission: users may edit their own profile; Admins may edit any."""

    def has_object_permission(self, request, view, obj):
        if request.user.is_superuser or _role(request) == "ADMIN":
            return True
        return obj.id == request.user.id
