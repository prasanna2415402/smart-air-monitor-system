from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.core.validators import RegexValidator
from django.db import models

from apps.accounts.managers import UserManager

mobile_validator = RegexValidator(
    regex=r"^[0-9+\-\s()]{10,20}$",
    message="Please enter a valid mobile number.",
)


def profile_photo_path(instance, filename):
    return f"profile_photos/{instance.username}/{filename}"


class User(AbstractBaseUser, PermissionsMixin):
    """
    Custom user model matching the fields captured by the original
    Smart Air Monitor signup form (see src/db/schema.ts in the frontend):
    fullName, username, email, mobileNumber, employeeId, role, password,
    accountStatus, registrationDate, lastUpdated, isActive, profilePhoto.
    """

    class Role(models.TextChoices):
        ADMIN = "ADMIN", "Admin"
        OPERATOR = "OPERATOR", "Operator"
        VIEWER = "VIEWER", "Viewer"

    class AccountStatus(models.TextChoices):
        PENDING = "PENDING", "Pending"
        APPROVED = "APPROVED", "Approved"
        REJECTED = "REJECTED", "Rejected"
        SUSPENDED = "SUSPENDED", "Suspended"

    full_name = models.CharField(max_length=100)
    username = models.CharField(max_length=50, unique=True)
    email = models.EmailField(max_length=100, unique=True)
    mobile_number = models.CharField(max_length=20, validators=[mobile_validator])
    employee_id = models.CharField(max_length=50, blank=True, null=True)

    role = models.CharField(max_length=20, choices=Role.choices, default=Role.VIEWER)
    account_status = models.CharField(
        max_length=20, choices=AccountStatus.choices, default=AccountStatus.PENDING
    )

    registration_date = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    profile_photo = models.ImageField(upload_to=profile_photo_path, blank=True, null=True)

    approved_by = models.ForeignKey(
        "self", null=True, blank=True, on_delete=models.SET_NULL, related_name="approved_users"
    )
    approved_at = models.DateTimeField(null=True, blank=True)
    rejection_reason = models.CharField(max_length=255, blank=True, null=True)

    objects = UserManager()

    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = ["email", "full_name", "mobile_number"]

    class Meta:
        db_table = "users"
        ordering = ["-registration_date"]
        indexes = [
            models.Index(fields=["email"]),
            models.Index(fields=["role"]),
            models.Index(fields=["account_status"]),
        ]

    def __str__(self):
        return f"{self.username} ({self.role})"

    @property
    def is_approved(self):
        return self.account_status == self.AccountStatus.APPROVED


class RefreshTokenAudit(models.Model):
    """Optional audit trail of login/logout events for security review."""

    class Action(models.TextChoices):
        LOGIN = "LOGIN", "Login"
        LOGOUT = "LOGOUT", "Logout"
        REFRESH = "REFRESH", "Refresh"
        FAILED_LOGIN = "FAILED_LOGIN", "Failed Login"

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="auth_events", null=True, blank=True)
    action = models.CharField(max_length=20, choices=Action.choices)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "auth_events"
        ordering = ["-created_at"]
