from app.bot.utils import normalize_url, validate_url

def test_normalize_and_validate():
    """
    Unit-тесты для функций normalize_url и validate_url.

    Проверяет:
    - автоматическое добавление http://, если схема отсутствует
    - корректную валидацию http/https URL
    - отбраковку некорректных строк
    """
    # URL без схемы → должен получить http://
    assert normalize_url("example.com") == "http://example.com"

    # Валидные адреса
    assert validate_url("http://example.com")
    assert validate_url("https://example.com")

    # Невалидный ввод
    assert not validate_url("not a url")

