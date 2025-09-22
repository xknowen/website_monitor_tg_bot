"""
Главная точка входа в приложение.

Запускает Telegram-бота и сервис мониторинга сайтов параллельно
в рамках одного asyncio-цикла.
"""

import asyncio
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from app.core.config import settings
from app.core.logger import get_logger
from app.bot.handlers import router
from app.db.database import engine, Base
from app.core.scheduler import start_scheduler, schedule_all
from app.services.monitor import start_monitor  # импортируем монитор

logger = get_logger()


async def init_db():
    """
    Инициализация базы данных:
    создаёт все таблицы при старте приложения.
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def start_bot():
    """
    Запуск Telegram-бота.
    """
    logger.info("Starting bot")
    bot = Bot(token=settings.BOT_TOKEN)
    dp = Dispatcher(storage=MemoryStorage())
    dp.include_router(router)

    # Планируем все задачи в мониторинг и запускаем планировщик
    await schedule_all()
    start_scheduler()

    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()


async def main():
    """
    Основная функция:
    запускает БД, бота и монитор параллельно.
    """
    await init_db()

    # Запускаем бота и монитор параллельно
    await asyncio.gather(
        start_bot(),
        start_monitor(),  # сервис мониторинга
    )


if __name__ == "__main__":
    asyncio.run(main())
