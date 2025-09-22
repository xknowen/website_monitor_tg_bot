from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger

from app.core.logger import get_logger
from app.db.database import AsyncSessionLocal
from app.db import crud
from app.services.monitor import check_site
from app.services.notifier import notify_user

logger = get_logger()
scheduler = AsyncIOScheduler()


async def job_wrapper(site_id: int, chat_id: int | None = None) -> None:
    """
    Задача для планировщика: проверяет сайт и отправляет уведомление при сбое.

    Args:
        site_id (int): Идентификатор сайта в БД.
        chat_id (int | None): ID чата для отправки уведомлений (если указан).
    """
    async with AsyncSessionLocal() as session:
        site = await crud.get_site(session, site_id)
        if not site or not site.is_active:
            return

        res = await check_site(session, site)

        # Уведомляем пользователя, если сайт недоступен
        if not res["is_available"] and chat_id:
            await notify_user(chat_id, f"[ALERT] {site.url} is down")


async def schedule_all() -> None:
    """
    Планирует задачи для всех сайтов из базы данных.
    """
    async with AsyncSessionLocal() as session:
        sites = await crud.list_sites(session)

    for s in sites:
        scheduler.add_job(
            job_wrapper,
            IntervalTrigger(seconds=s.interval),
            args=[s.id],
            id=str(s.id),
            replace_existing=True,
        )
        logger.info(f"Scheduled job for {s.url} every {s.interval}s")


def start_scheduler() -> None:
    """
    Запускает планировщик.
    """
    scheduler.start(paused=False)
    logger.info("Scheduler started")

