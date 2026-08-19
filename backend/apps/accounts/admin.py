from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin

from apps.accounts.models import RefreshTokenAudit, User


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    model = User
    ordering = ["-registration_date"]
    list_display = [
        "username", "full_name", "email", "role", "account_status",
        "is_active", "registration_date",
    ]
    list_filter = ["role", "account_status", "is_active"]
    search_fields = ["username", "full_name", "email", "employee_id"]
    readonly_fields = ["registration_date", "last_updated"]

    fieldsets = (
        (None, {"fields": ("username", "password")}),
        ("Personal Info", {"fields": ("full_name", "email", "mobile_number", "employee_id", "profile_photo")}),
        ("Role & Status", {"fields": ("role", "account_status", "is_active", "rejection_reason", "approved_by", "approved_at")}),
        ("Permissions", {"fields": ("is_staff", "is_superuser", "groups", "user_permissions")}),
        ("Important dates", {"fields": ("last_login", "registration_date", "last_updated")}),
    )
    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("username", "email", "full_name", "mobile_number", "role", "password1", "password2"),
        }),
    )


@admin.register(RefreshTokenAudit)
class RefreshTokenAuditAdmin(admin.ModelAdmin):
    list_display = ["user", "action", "ip_address", "created_at"]
    list_filter = ["action"]
    readonly_fields = [f.name for f in RefreshTokenAudit._meta.fields]

    def has_add_permission(self, request):
        return False
