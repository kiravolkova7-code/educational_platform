import django_filters
from .models import Payment


class PaymentFilter(django_filters.FilterSet):
    course = django_filters.NumberFilter(field_name="paid_course", label="ID курса")
    lesson = django_filters.NumberFilter(field_name="paid_lesson", label="ID урока")
    method = django_filters.CharFilter(field_name="method", lookup_expr="exact", label="Способ оплаты")
    status = django_filters.CharFilter(field_name="status", lookup_expr="exact", label="Статус платежа")

    has_payment_url = django_filters.BooleanFilter(
        field_name='payment_url',
        lookup_expr='isnull',
        exclude=True,
        label='Есть ссылка на оплату'
    )

    class Meta:
        model = Payment
        fields = []