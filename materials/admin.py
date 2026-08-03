from django.contrib import admin
from .models import Course, Lesson


class LessonInline(admin.StackedInline):
    """
    Встроенный редактор уроков внутри страницы Курса.
    Использование TabularInline сделает таблицу более компактной,
    но StackedInline дает больше места для текстовых полей description.
    """

    model = Lesson
    extra = 0  # Не показывать пустые строки для новых уроков по умолчанию
    fields = (
        "title",
        "preview",
        "description",
        "video_url",
        "order",
        "created_at",
        "updated_at",
    )
    readonly_fields = ("created_at", "updated_at")
    ordering = ("order",)


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ("title", "created_at", "update_at")
    search_fields = ("title", "description")
    list_filter = ("created_at", "update_at")

    inlines = [LessonInline]  # Подключаем редактор уроков сюда

    fieldsets = (
        (None, {"fields": ("title", "preview", "description")}),
        (
            "Даты",
            {
                "fields": ("created_at", "update_at"),
                "classes": ("collapse",),  # Сворачиваемая секция
            },
        ),
    )
    readonly_fields = ("created_at", "update_at")


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ("__str__", "course", "order", "created_at", "updated_at")
    list_filter = ("course", "created_at", "updated_at")
    search_fields = ("title", "description", "course__title")
    ordering = ("course", "order")

    fieldsets = (
        (
            None,
            {
                "fields": (
                    "course",
                    "title",
                    "preview",
                    "description",
                    "video_url",
                    "order",
                )
            },
        ),
        (
            "Даты",
            {
                "fields": ("created_at", "updated_at"),
                "classes": ("collapse",),
            },
        ),
    )
    readonly_fields = ("created_at", "updated_at")
