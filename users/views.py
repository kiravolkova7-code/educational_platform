
from rest_framework import viewsets, status
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter

from .models import Payment, User
from .permissions import IsOwnerOrModerator
from .serializers import PaymentSerializer
from .filters import PaymentFilter
from rest_framework import generics, permissions
from rest_framework.response import Response
from .serializers import UserProfileSerializer, UserAvatarUpdateSerializer, RegisterSerializer

class ProfileRetrieveUpdateView(generics.RetrieveUpdateAPIView):
    serializer_class = UserProfileSerializer
    permission_classes = [IsOwnerOrModerator]

    def get_object(self):
        if not self.request.user.is_authenticated:
            raise PermissionError("Требуется вход")
        return self.request.user

class AvatarUpdateView(generics.UpdateAPIView):
    """PATCH /api/profile/avatar/ — быстрая смена аватара без пересылки всех полей"""
    serializer_class = UserAvatarUpdateSerializer
    permission_classes = [IsOwnerOrModerator]

    def get_object(self):
        if not self.request.user.is_authenticated:
            raise PermissionError("Требуется вход")
        return self.request.user

    def partial_update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(UserProfileSerializer(instance).data)


class PaymentViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_class = PaymentFilter
    ordering_fields = ['payment_date']

    def get_queryset(self):
        return Payment.objects.all()


class RegisterView(generics.CreateAPIView):
    """Регистрация нового пользователя с проверкой дубликатов."""
    queryset = User.objects.all()
    permission_classes = [permissions.AllowAny]
    serializer_class = RegisterSerializer

    def create(self, request, *args, **kwargs):
        try:
            return super().create(request, *args, **kwargs)
        except Exception as e:
            if 'email' in str(e).lower():
                return Response(
                    {'error': 'Пользователь с таким Email уже существует.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)