import sys
import os
from loguru import logger

# Создаём папку для логов, если её нет
os.makedirs("logs", exist_ok=True)

# Убираем стандартный хендлер и настраиваем свои
logger.remove()
logger.add(sys.stdout, level="INFO")  # вывод в консоль
logger.add(
    "logs/site_monitor.log",
    rotation="10 MB",       # ротация при достижении 10 MB
    retention="10 days",    # хранение логов 10 дней
    level="DEBUG",          # уровень логирования
)


def get_logger():
    """
    Возвращает настроенный экземпляр логгера Loguru.

    Returns:
        logger: Экземпляр логгера.
    """
    return logger
