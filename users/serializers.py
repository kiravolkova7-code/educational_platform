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


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('email', 'password', 'phone', 'city')

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Этот email уже занят.")
        return value

    def create(self, validated_data):
        user = User.objects.create_user(
            email=validated_data['email'],
            password=validated_data['password'],
            phone=validated_data.get('phone'),
            city=validated_data.get('city')
        )
        return user