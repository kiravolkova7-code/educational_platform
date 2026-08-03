import logging
from datetime import timedelta
from django.utils import timezone
from django.contrib.auth import get_user_model

from config.celery import app

logger = logging.getLogger(__name__)
User = get_user_model()


@app.task(bind=True)
def deactivate_inactive_users(self):
    """
    Блокирует пользователей, которые не заходили в систему более месяца.
    """
    try:
        threshold_date = timezone.now() - timedelta(days=30)

        users_to_deactivate = User.objects.filter(
            is_active=True, last_login__lt=threshold_date
        )

        count = users_to_deactivate.count()
        if count == 0:
            logger.info(
                "Задача деактивации: не найдено пользователей для блокировки."
            )
            return {"status": "no_changes"}

        updated_count = users_to_deactivate.update(is_active=False)

        user_ids = list(users_to_deactivate.values_list("id", flat=True))
        logger.warning(
            f"Деактивировано {updated_count} пользователей за неактивность: IDs {user_ids}"
        )

        return {"status": "success", "deactivated_count": updated_count}

    except Exception as exc:
        logger.error(
            f"Ошибка в задаче deactivate_inactive_users: {exc}", exc_info=True
        )
        raise
