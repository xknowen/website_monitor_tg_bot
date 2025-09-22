from aiogram import Bot
from app.core.config import settings
from app.core.logger import get_logger

logger = get_logger()
bot = Bot(token=settings.BOT_TOKEN)


async def notify_user(chat_id: int, text: str) -> None:
    """
    Отправляет уведомление пользователю в Telegram.

    Args:
        chat_id (int): ID чата пользователя.
        text (str): Текст уведомления.
    """
    try:
        # Отправляем сообщение пользователю
        await bot.send_message(chat_id, text)
        logger.info(f'Notified {chat_id}: {text}')
    except Exception as err:
        # Логируем ошибку, если сообщение не удалось отправить
        logger.exception(f'Failed notify {chat_id}: {err}')
