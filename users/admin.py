from .models import Payment
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django import forms

from .models import User


class UserCreationForm(forms.ModelForm):
    """
    Форма для создания нового пользователя через админку.
    Требует ввода email и пароля.
    """
    password1 = forms.CharField(label='Пароль', widget=forms.PasswordInput)
    password2 = forms.CharField(
        label='Подтверждение пароля',
        widget=forms.PasswordInput,
        help_text='Введите тот же пароль, что и выше, для проверки.'
    )

    class Meta:
        model = User
        fields = ('email', 'first_name', 'last_name', 'phone', 'city')

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Пароли не совпадают.")
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
    Пароль отображается в виде хэша (только для чтения).
    """
    password = ReadOnlyPasswordHashField(
        label='Пароль',
        help_text='Изменить пароль можно по этой ссылке: <a href="../../password/">Сменить пароль</a>.'
    )

    class Meta:
        model = User
        # Исключаем авто-поля из формы редактирования
        exclude = ('created_at', 'update_at')

    def clean_password(self):
        return self.initial["password"]


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    add_form = UserCreationForm
    form = UserChangeForm

    list_display = ('email', 'first_name', 'last_name', 'is_staff', 'created_at')
    list_filter = ('is_staff', 'is_superuser', 'is_active')

    # Убрали created_at и update_at отсюда
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Персональные данные', {'fields': ('first_name', 'last_name', 'avatar', 'phone', 'city')}),
        ('Права доступа', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Важные даты', {'fields': ('last_login',)}),  # Оставили last_login, он редактируемый
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2'),
        }),
    )

    search_fields = ('email', 'first_name', 'last_name')
    ordering = ('-created_at',)

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('user', 'payment_date', 'amount', 'method', 'paid_course', 'paid_lesson')
    list_filter = ('method', 'payment_date')
    search_fields = ('user__email', 'amount')
