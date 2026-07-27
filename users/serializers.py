from .models import Payment
from rest_framework import serializers
from .models import User

class UserProfileSerializer(serializers.ModelSerializer):
    """
    Сериализатор для просмотра и частичного обновления профиля.
    Поля first_name и last_name берутся из родительской AbstractBaseUser.
    Пароль исключен намеренно — для смены используйте отдельный эндпоинт.
    """
    class Meta:
        model = User
        fields = ('email', 'first_name', 'last_name', 'phone', 'city', 'avatar')
        read_only_fields = ('email',)

class UserAvatarUpdateSerializer(serializers.ModelSerializer):
    """Отдельный легковесный сериализатор только для загрузки аватара."""
    class Meta:
        model = User
        fields = ('avatar',)


class PaymentSerializer(serializers.ModelSerializer):
    user_email = serializers.ReadOnlyField(source='user.email')

    class Meta:
        model = Payment
        fields = [
            'id', 'user', 'user_email', 'payment_date',
            'paid_course', 'paid_lesson', 'amount', 'method'
        ]
        read_only_fields = ['user', 'payment_date']