"""
Модуль с обработчиками команд и колбэков Telegram-бота
для управления мониторингом сайтов.
"""

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery

from app.db.database import AsyncSessionLocal
from app.db import crud
from app.bot.keyboards import site_item_kb
from app.bot.utils import normalize_url, validate_url
from app.core.logger import get_logger
from app.core.config import settings

router = Router()
logger = get_logger()


@router.message(Command("start"))
async def cmd_start(message: Message):
    """
    Команда /start — приветственное сообщение.
    """
    await message.answer(
        "Привет! Я бот для мониторинга сайтов. "
        "Используй /add <url> [interval], /list, /remove <id>, /report, /history <id>"
    )


@router.message(Command("add"))
async def cmd_add(message: Message):
    """
    Команда /add — добавить сайт в мониторинг.

    Формат:
        /add <url> [interval_seconds]
    """
    args = message.text.split()
    if len(args) < 2:
        await message.answer("Использование: /add <url> [interval_seconds]")
        return

    url = normalize_url(args[1])
    if not validate_url(url):
        await message.answer("Неверный URL")
        return

    interval = int(args[2]) if len(args) > 2 else settings.DEFAULT_INTERVAL

    async with AsyncSessionLocal() as session:
        site = await crud.create_site(session, url, interval)

    await message.answer(
        f"Сайт добавлен: {site.id} — {site.url} (интервал {site.interval}s)"
    )


@router.message(Command("list"))
async def cmd_list(message: Message):
    """
    Команда /list — показать список отслеживаемых сайтов.
    """
    async with AsyncSessionLocal() as session:
        sites = await crud.list_sites(session)

    if not sites:
        await message.answer("Список пуст")
        return

    for s in sites:
        await message.answer(
            f"{s.id}: {s.url} (интервал {s.interval}s)",
            reply_markup=site_item_kb(s.id),
        )


@router.callback_query(lambda c: c.data and c.data.startswith("del:"))
async def cb_delete(call: CallbackQuery):
    """
    Обработка колбэка "Удалить сайт" из списка.
    """
    site_id = int(call.data.split(":")[1])
    async with AsyncSessionLocal() as session:
        await crud.delete_site(session, site_id)

    await call.message.edit_text(f"Сайт {site_id} удалён")


@router.message(Command("remove"))
async def cmd_remove(message: Message):
    """
    Команда /remove — удалить сайт по ID.
    """
    parts = message.text.split()
    if len(parts) < 2:
        await message.answer("Использование: /remove <id>")
        return

    site_id = int(parts[1])
    async with AsyncSessionLocal() as session:
        await crud.delete_site(session, site_id)

    await message.answer(f"Сайт {site_id} удалён")


@router.message(Command("history"))
async def cmd_history(message: Message):
    """
    Команда /history — последние проверки сайта.

    Формат:
        /history <site_id>
    """
    parts = message.text.split()
    if len(parts) < 2:
        await message.answer("Использование: /history <site_id>")
        return

    site_id = int(parts[1])
    async with AsyncSessionLocal() as session:
        checks = await crud.last_checks(session, site_id, limit=10)

    if not checks:
        await message.answer("Нет проверок для этого сайта")
        return

    text = "Последние проверки:\n"
    for c in checks:
        text += (
            f"{c.checked_at} — "
            f"{'UP' if c.is_available else 'DOWN'} — "
            f"status={c.status_code} — "
            f"time={c.response_time}\n"
        )

    await message.answer(text)


@router.message(Command("report"))
async def cmd_report(message: Message):
    """
    Команда /report — общий отчёт по всем сайтам.
    """
    async with AsyncSessionLocal() as session:
        sites = await crud.list_sites(session)

        text = "Отчёт по сайтам:\n"
        for s in sites:
            st = await crud.stats_for_site(session, s.id)
            text += (
                f"{s.id}: {s.url} — "
                f"Uptime={st['uptime']}% — "
                f"Avg response={st['average_response']}s\n"
            )

    await message.answer(text)

