import django_filters
from .models import Payment

class PaymentFilter(django_filters.FilterSet):
    course = django_filters.NumberFilter(field_name="paid_course", label="ID курса")
    lesson = django_filters.NumberFilter(field_name="paid_lesson", label="ID урока")
    method = django_filters.CharFilter(field_name="method", lookup_expr="exact", label="Способ оплаты")

    class Meta:
        model = Payment
        fields = []