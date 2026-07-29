from django.db import models

from django.conf import settings


class Course(models.Model):
    title = models.CharField(max_length=100, verbose_name='Название')
    preview = models.ImageField(upload_to='courses/previews/', verbose_name='Превью', blank=True, null=True)
    description = models.TextField(verbose_name='Описание',  help_text='Максимум 500 символов', blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    update_at = models.DateTimeField(auto_now=True, verbose_name='Дата обновления')

    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='courses', verbose_name='Владелец', blank=True, null=True)

    stripe_product_id = models.CharField(
        max_length=255,
        verbose_name='ID продукта в Stripe',
        blank=True,
        null=True,
        unique=True,
        help_text='Заполняется автоматически при создании цены'
    )

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Курс'
        verbose_name_plural = 'Курсы'
        ordering = ['-created_at']


class Lesson(models.Model):
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='lessons',
        verbose_name='Курс'
    )
    title = models.CharField(max_length=200, verbose_name='Название урока')
    preview = models.ImageField(
        upload_to='lessons/previews/',
        verbose_name='Превью урока',
        blank=True,
        null=True
    )
    description = models.TextField(verbose_name='Описание урока', blank=True, null=True)
    video_url = models.URLField(verbose_name='Ссылка на видео', max_length=500, blank=True)

    order = models.PositiveSmallIntegerField(default=1, verbose_name='Порядок отображения')

    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата добавления')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата изменения')

    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='lessons', verbose_name='Владелец', blank=True, null=True)

    def __str__(self):
        return f"{self.course.title} — {self.title}"

    class Meta:
        verbose_name = 'Урок'
        verbose_name_plural = 'Уроки'
        ordering = ['order', 'created_at']
        constraints = [
            models.UniqueConstraint(
                fields=['course', 'order'],
                name='unique_lesson_order_per_course'
            )
        ]
