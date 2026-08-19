from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.accounts.views import (
    ChangePasswordView,
    CustomTokenRefreshView,
    LoginView,
    LogoutView,
    ProfileView,
    RegisterView,
    UserViewSet,
)

router = DefaultRouter()
router.register("users", UserViewSet, basename="user")

urlpatterns = [
    path("auth/register/", RegisterView.as_view(), name="auth-register"),
    path("auth/login/", LoginView.as_view(), name="auth-login"),
    path("auth/logout/", LogoutView.as_view(), name="auth-logout"),
    path("auth/token/refresh/", CustomTokenRefreshView.as_view(), name="auth-token-refresh"),
    path("profile/me/", ProfileView.as_view(), name="profile-me"),
    path("profile/change-password/", ChangePasswordView.as_view(), name="profile-change-password"),
    path("", include(router.urls)),
]
