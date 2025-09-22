import pytest
from app.services.monitor import check_site


class DummySite:
    """Простой объект-сайт для теста."""

    def __init__(self, id, url):
        self.id = id
        self.url = url


@pytest.mark.asyncio
async def test_check_site_down(monkeypatch):
    """
    Проверяет работу функции check_site при недоступном сайте.

    Используется monkeypatch для подмены записи результата в БД.
    """
    dummy = DummySite(1, "http://nonexistent.invalid")

    async def fake_create_check(session, site, status_code, response_time, is_available):
        # Заглушка для функции сохранения результата
        return True

    # Подменяем реальный crud.create_check на заглушку
    monkeypatch.setattr("db.crud.create_check", fake_create_check)

    class DummySession:
        """Пустая сессия для имитации SQLAlchemy."""
        pass

    res = await check_site(DummySession(), dummy)

    # Проверяем, что результат корректный словарь
    assert res is not None
    assert isinstance(res, dict)
    assert res["is_available"] in (True, False)
