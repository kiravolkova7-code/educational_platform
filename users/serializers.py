from rest_framework import serializers
from .models import Payment

class PaymentSerializer(serializers.ModelSerializer):
    # Чтобы видеть почту пользователя без создания отдельного UserSerializer
    user_email = serializers.ReadOnlyField(source='user.email')

    class Meta:
        model = Payment
        fields = [
            'id', 'user', 'user_email', 'payment_date',
            'paid_course', 'paid_lesson', 'amount', 'method'
        ]
        read_only_fields = ['user', 'payment_date']