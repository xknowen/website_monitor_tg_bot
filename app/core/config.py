from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    Настройки приложения, загружаемые из переменных окружения или файла .env.

    Атрибуты:
        BOT_TOKEN (str): Токен Telegram-бота.
        DATABASE_URL (str): URL подключения к базе данных.
        CHECK_TIMEOUT (int): Таймаут проверки сайта (секунды).
        DEFAULT_INTERVAL (int): Интервал проверки сайтов по умолчанию (секунды).
    """
    BOT_TOKEN: str
    DATABASE_URL: str = 'sqlite+aiosqlite:///./site_monitor.db'
    CHECK_TIMEOUT: int = 10
    DEFAULT_INTERVAL: int = 60

    class Config:
        env_file = ".env"  # загружаем настройки из файла .env


# Глобальный экземпляр настроек
settings = Settings()

