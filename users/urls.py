from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .apps import UsersConfig
from .views import PaymentViewSet, ProfileRetrieveUpdateView, AvatarUpdateView

app_name = UsersConfig.name

router = DefaultRouter()
router.register(r'payments', PaymentViewSet, basename='payment')

urlpatterns = [
    path('profile/', ProfileRetrieveUpdateView.as_view(), name='profile-detail'),
    path('profile/avatar/', AvatarUpdateView.as_view(), name='avatar-update'),
    path('', include(router.urls)),
]