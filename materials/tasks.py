from celery import shared_task
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.urls import reverse
from django.conf import settings


@shared_task(bind=True)
def send_course_update_email(self, user_email, course_id, course_title):
    """
    Асинхронная задача по отправке уведомления об обновлении курса.
    bind=True позволяет обращаться к self.request.id для логирования.
    """
    try:
        course_url = f"{settings.SITE_URL}{reverse('course_detail', args=[course_id])}"

        context = {
            'user_email': user_email,
            'course_title': course_title,
            'course_url': course_url,
        }

        subject = f'[Обновление] В курсе "{course_title}" появились новые материалы'

        html_message = render_to_string('emails/course_update.html', context)

        plain_message = strip_tags(html_message)

        from_email = settings.DEFAULT_FROM_EMAIL

        send_mail(
            subject=subject,
            message=plain_message,
            from_email=from_email,
            recipient_list=[user_email],
            html_message=html_message,
            fail_silently=False,
        )
        return {'status': 'success', 'task_id': self.request.id}
    except Exception as exc:
        raise self.retry(exc=exc, countdown=300, max_retries=3)