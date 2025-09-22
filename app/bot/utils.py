from urllib.parse import urlparse


def normalize_url(url: str) -> str:
    """
    Приводит URL к нормализованному виду:
    добавляет http://, если протокол не указан.

    Args:
        url (str): Введённый пользователем адрес.

    Returns:
        str: Нормализованный URL.
    """
    if not url.startswith("http://") and not url.startswith("https://"):
        url = "http://" + url
    return url


def validate_url(url: str) -> bool:
    """
    Проверяет корректность URL.

    Args:
        url (str): Адрес для проверки.

    Returns:
        bool: True, если URL корректный, иначе False.
    """
    try:
        p = urlparse(url)
        return all([p.scheme in ("http", "https"), p.netloc])
    except Exception:
        return False
