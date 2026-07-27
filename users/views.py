from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter

from .models import Payment, User
from .permissions import IsOwnerOrModerator
from .serializers import PaymentSerializer, UserSerializer
from .filters import PaymentFilter
from rest_framework import generics, permissions, viewsets, status
from rest_framework.response import Response
from .serializers import UserProfileSerializer, UserAvatarUpdateSerializer, RegisterSerializer

class ProfileRetrieveUpdateView(generics.RetrieveUpdateAPIView):
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user

class AvatarUpdateView(generics.UpdateAPIView):
    serializer_class = UserAvatarUpdateSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
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



class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if self.request.user.is_staff:
            return User.objects.all()
        return User.objects.filter(pk=self.request.user.pk)

    def get_permissions(self):
        if self.action in ['list', 'retrieve', 'update', 'partial_update']:
            return [permissions.IsAuthenticated()]
        if self.action == 'destroy':
            return [permissions.IsAdminUser()]
        return super().get_permissions()
