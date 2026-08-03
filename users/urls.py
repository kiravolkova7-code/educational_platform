from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .apps import UsersConfig
from .views import (
    PaymentViewSet,
    ProfileRetrieveUpdateView,
    AvatarUpdateView,
    RegisterView,
    UserViewSet,
)
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

app_name = UsersConfig.name

router = DefaultRouter()
router.register(r"payments", PaymentViewSet, basename="payment")
router.register(r"users", UserViewSet, basename="user")

urlpatterns = [
    # Регистрация и получение токенов
    path("register/", RegisterView.as_view(), name="register"),
    path("token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    # Профиль
    path(
        "profile/", ProfileRetrieveUpdateView.as_view(), name="profile-detail"
    ),
    path("profile/avatar/", AvatarUpdateView.as_view(), name="avatar-update"),
    path("", include(router.urls)),
]
