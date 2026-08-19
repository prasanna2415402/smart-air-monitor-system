from django.contrib.auth import authenticate, password_validation
from django.core import exceptions as django_exceptions
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from apps.accounts.models import User


class RegisterSerializer(serializers.ModelSerializer):
    """
    Mirrors the original signup form 1:1: fullName, username, email,
    mobileNumber, employeeId, password, confirmPassword, role, profilePhoto,
    termsAccepted. New accounts are always created with status=PENDING and
    is_active=False, awaiting Admin approval.
    """

    confirm_password = serializers.CharField(write_only=True)
    terms_accepted = serializers.BooleanField(write_only=True)
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = [
            "id", "full_name", "username", "email", "mobile_number", "employee_id",
            "password", "confirm_password", "role", "profile_photo", "terms_accepted",
        ]
        extra_kwargs = {
            "profile_photo": {"required": False},
            "employee_id": {"required": False},
            "role": {"required": False},
        }

    def validate_role(self, value):
        # Self-registration may only request Operator or Viewer; Admin role
        # must be granted explicitly by an existing Admin after approval.
        if value == User.Role.ADMIN:
            raise serializers.ValidationError(
                "The Admin role cannot be self-assigned during signup."
            )
        return value

    def validate_terms_accepted(self, value):
        if not value:
            raise serializers.ValidationError("You must accept the terms and conditions.")
        return value

    def validate(self, attrs):
        if attrs["password"] != attrs.pop("confirm_password"):
            raise serializers.ValidationError({"confirm_password": "Passwords don't match"})
        try:
            password_validation.validate_password(attrs["password"])
        except django_exceptions.ValidationError as exc:
            raise serializers.ValidationError({"password": list(exc.messages)})
        return attrs

    def create(self, validated_data):
        validated_data.pop("terms_accepted", None)
        password = validated_data.pop("password")
        user = User(**validated_data)
        user.set_password(password)
        user.account_status = User.AccountStatus.PENDING
        user.is_active = False
        user.role = validated_data.get("role") or User.Role.VIEWER
        user.save()
        return user


class LoginSerializer(TokenObtainPairSerializer):
    """
    Extends SimpleJWT's obtain-pair serializer to (a) accept email OR
    username, (b) enforce the Pending-approval gate from the original
    login page, and (c) embed role/profile info in the token response.
    """

    username_field = User.USERNAME_FIELD

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["identifier"] = serializers.CharField(write_only=True)
        self.fields.pop(self.username_field, None)
        self.fields.pop("password", None)
        self.fields["password"] = serializers.CharField(write_only=True)

    def validate(self, attrs):
        identifier = attrs.get("identifier")
        password = attrs.get("password")

        user = User.objects.filter(email__iexact=identifier).first() or User.objects.filter(
            username__iexact=identifier
        ).first()

        if user is None or not user.check_password(password):
            raise serializers.ValidationError(
                "Invalid credentials. Please check your email/username and password."
            )

        if user.account_status == User.AccountStatus.PENDING:
            raise serializers.ValidationError(
                "Your account is pending Admin approval. Please try again later."
            )
        if user.account_status == User.AccountStatus.REJECTED:
            raise serializers.ValidationError(
                "Your registration was rejected. Please contact your administrator."
            )
        if user.account_status == User.AccountStatus.SUSPENDED:
            raise serializers.ValidationError(
                "Your account has been suspended. Please contact your administrator."
            )
        if not user.is_active:
            raise serializers.ValidationError("This account is inactive.")

        authenticate_user = authenticate(
            username=user.username, password=password
        )
        if authenticate_user is None:
            raise serializers.ValidationError("Invalid credentials.")

        refresh = self.get_token(user)
        data = {
            "refresh": str(refresh),
            "access": str(refresh.access_token),
            "user": UserSerializer(user).data,
        }
        return data

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token["role"] = user.role
        token["full_name"] = user.full_name
        token["email"] = user.email
        return token


class UserSerializer(serializers.ModelSerializer):
    """Full user representation for admin user-management screens."""

    class Meta:
        model = User
        fields = [
            "id", "full_name", "username", "email", "mobile_number", "employee_id",
            "role", "account_status", "is_active", "profile_photo",
            "registration_date", "last_updated", "approved_at", "rejection_reason",
        ]
        read_only_fields = ["id", "registration_date", "last_updated", "approved_at"]


class UserAdminUpdateSerializer(serializers.ModelSerializer):
    """Admin-only: change role, account status, or active flag for any user."""

    class Meta:
        model = User
        fields = ["role", "account_status", "is_active", "rejection_reason"]

    def validate(self, attrs):
        status = attrs.get("account_status")
        if status == User.AccountStatus.REJECTED and not attrs.get("rejection_reason"):
            raise serializers.ValidationError(
                {"rejection_reason": "A reason is required when rejecting a user."}
            )
        return attrs


class ProfileSerializer(serializers.ModelSerializer):
    """Self-service profile view/update (excludes role & account_status)."""

    class Meta:
        model = User
        fields = [
            "id", "full_name", "username", "email", "mobile_number",
            "employee_id", "role", "account_status", "profile_photo",
            "registration_date", "last_updated",
        ]
        read_only_fields = ["id", "username", "role", "account_status", "registration_date", "last_updated"]


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True)
    confirm_new_password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        if attrs["new_password"] != attrs["confirm_new_password"]:
            raise serializers.ValidationError({"confirm_new_password": "Passwords don't match"})
        try:
            password_validation.validate_password(attrs["new_password"])
        except django_exceptions.ValidationError as exc:
            raise serializers.ValidationError({"new_password": list(exc.messages)})
        return attrs

    def validate_old_password(self, value):
        user = self.context["request"].user
        if not user.check_password(value):
            raise serializers.ValidationError("Current password is incorrect.")
        return value
