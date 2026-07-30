from django.contrib import admin
from .models import User, Payment
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django import forms
from django.core.exceptions import ValidationError

from django.urls import reverse
from django.utils.html import format_html
from .models import Payment



class UserCreationForm(forms.ModelForm):
    password1 = forms.CharField(label='Пароль', widget=forms.PasswordInput)
    password2 = forms.CharField(
        label='Подтверждение пароля',
        widget=forms.PasswordInput,
        help_text='Введите тот же пароль, что и выше, для проверки.'
    )

    class Meta:
        model = User
        fields = ('email', 'phone', 'city')

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise ValidationError("Пароли не совпадают.")
        return password2

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


class UserChangeForm(forms.ModelForm):
    """
    Форма для изменения существующего пользователя.
    """
    password = ReadOnlyPasswordHashField(
        label='Пароль',
        help_text='Изменить пароль можно по этой ссылке: <a href="../../password/">Сменить пароль</a>.'
    )

    class Meta:
        model = User
        exclude = ('created_at', 'update_at')

    def clean_password(self):
        return self.initial["password"]


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    add_form = UserCreationForm
    form = UserChangeForm

    list_display = ('email', 'phone', 'city', 'is_staff', 'is_active', 'created_at')
    list_filter = ('is_staff', 'is_superuser', 'is_active')

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Персональные данные', {'fields': ('avatar', 'phone', 'city')}),
        ('Права доступа', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')
        }),
        ('Важные даты', {'fields': ('last_login',)}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2'),
        }),
    )

    search_fields = ('email',)
    ordering = ('-created_at',)
    readonly_fields = ('last_login',)
    filter_horizontal = ('groups', 'user_permissions',)


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    """
    Админ-панель для платежей.
    """

    # Поля в списке объектов
    list_display = (
        'user_email_link',
        'paid_course_title',
        'amount_rub',
        'payment_url_link',
        'created_at'
    )

    list_filter = ('created_at', 'paid_course')

    search_fields = ('user__email', 'paid_course__title')

    readonly_fields = ('payment_url', 'created_at', 'user_email_static')

    date_hierarchy = 'created_at'

    @admin.display(description='Email пользователя', ordering='user__email')
    def user_email_link(self, obj):
        """Кликабельный email со ссылкой на профиль пользователя"""
        if obj.user:
            url = reverse("admin:users_user_change", args=[obj.user.pk])
            return format_html('<a href="{}">{}</a>', url, obj.user.email)
        return '-'

    @admin.display(description='Email (стат.)')
    def user_email_static(self, obj):
        """Статичный email внутри формы платежа (для copy-paste)"""
        return obj.user.email if obj.user else '-'

    @admin.display(description='Курс', ordering='paid_course__title')
    def paid_course_title(self, obj):
        """Название курса вместо ID"""
        return obj.paid_course.title if obj.paid_course else '-'

    @admin.display(description='Ссылка на оплату')
    def payment_url_link(self, obj):
        """Кнопка-ссылка для быстрого перехода к Checkout Stripe из админки"""
        if obj.payment_url:
            return format_html(
                '<a class="button" href="{}" target="_blank" rel="noopener">Перейти к оплате</a>',
                obj.payment_url
            )
        return '-'