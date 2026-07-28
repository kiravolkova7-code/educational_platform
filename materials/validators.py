import re
from urllib.parse import urlparse
from django.core.exceptions import ValidationError

ALLOWED_DOMAINS = ['youtube.com', 'www.youtube.com', 'youtu.be']
YOUTUBE_SHORT_REGEX = re.compile(r'^(https?://)?(www\.)?youtu\.be/')


def extract_domain(url: str) -> str | None:
    """
    Извлекает чистый домен из URL без учета порта.
    Возвращает None, если ссылка пустая или не является HTTP(S).
    """
    if not url:
        return None

    try:
        parsed = urlparse(url)
        # Проверяем, что это веб-ссылка
        if parsed.scheme not in ('http', 'https'):
            return None

        domain = parsed.netloc.lower()
        if ':' in domain:
            domain = domain.split(':')[0]
        return domain
    except Exception:
        return None


def validate_youtube_only(value: str):
    """
    Валидатор, разрешающий только ссылки на youtube.com и youtu.be.
    """
    if not value:
        return

    domain = extract_domain(value)

    if not domain:
        raise ValidationError('Введите корректную ссылку.')

    is_short = bool(YOUTUBE_SHORT_REGEX.match(value))

    if domain not in ALLOWED_DOMAINS and not is_short:
        allowed_list = ', '.join(ALLOWED_DOMAINS)
        raise ValidationError(
            f'Разрешены только видео с YouTube ({allowed_list}). Ссылка на {domain} заблокирована.'
        )