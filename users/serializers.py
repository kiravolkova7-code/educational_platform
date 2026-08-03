from rest_framework import serializers
from .models import Payment, User

class UserProfileSerializer(serializers.ModelSerializer):
    """
    Сериализатор для просмотра и частичного обновления профиля.
    """

    first_name = serializers.CharField(
        source="profile.first_name", allow_blank=True, required=False
    )
    last_name = serializers.CharField(
        source="profile.last_name", allow_blank=True, required=False
    )

    class Meta:
        model = User
        fields = (
            "email",
            "first_name",
            "last_name",
            "phone",
            "city",
            "avatar",
        )
        read_only_fields = ("email",)


class UserAvatarUpdateSerializer(serializers.ModelSerializer):
    """Отдельный легковесный сериализатор только для загрузки аватара."""

    class Meta:
        model = User
        fields = ("avatar",)


class PaymentSerializer(serializers.ModelSerializer):
    user_email = serializers.ReadOnlyField(source="user.email")
    course_title = serializers.ReadOnlyField(source="paid_course.title")

    class Meta:
        model = Payment
        fields = [
            "id",
            "user",
            "user_email",
            "course_title",
            "paid_course",
            "amount_rub",
            "payment_url",
            "created_at",
        ]
        read_only_fields = ["user", "payment_url", "created_at", "amount_rub"]


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ("email", "password", "phone", "city")

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Этот email уже занят.")
        return value

    def create(self, validated_data):
        user = User.objects.create_user(
            email=validated_data["email"],
            password=validated_data["password"],
            phone=validated_data.get("phone"),
            city=validated_data.get("city"),
        )
        return user


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "email", "phone", "city", "avatar")
        read_only_fields = ("id", "email")
