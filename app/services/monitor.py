"""
Сервис мониторинга сайтов.

Запускается параллельно с ботом и периодически проверяет
доступность всех сайтов из базы данных.
"""

import asyncio
import httpx
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.db.database import AsyncSessionLocal
from app.db import crud
from app.core.logger import get_logger

logger = get_logger()


async def check_site(session: AsyncSession, site) -> dict:
    """
    Проверяет доступность сайта и сохраняет результат в базу.

    Args:
        session (AsyncSession): Сессия базы данных.
        site: Объект сайта с атрибутами `id` и `url`.

    Returns:
        dict: Результаты проверки:
            - site: объект сайта
            - status: код ответа (int или None)
            - response_time: время отклика в секундах (float или None)
            - is_available: доступность сайта (bool)
    """
    timeout = settings.CHECK_TIMEOUT
    url = site.url

    async with httpx.AsyncClient(timeout=timeout) as client:
        try:
            # Делаем HTTP-запрос к сайту
            response = await client.get(url)
            status = response.status_code
            elapsed = response.elapsed.total_seconds()
            is_available = 200 <= status < 400

            # Сохраняем результат в БД
            await crud.create_check(session, site, status, elapsed, is_available)
            logger.info(f"Checked {url}: {status} in {elapsed:.2f}s")

            return {
                "site": site,
                "status": status,
                "response_time": elapsed,
                "is_available": is_available,
            }

        except Exception as err:
            # Ошибка — считаем сайт недоступным
            logger.exception(f"Error checking {url}: {err}")
            await crud.create_check(session, site, None, None, False)

            return {
                "site": site,
                "status": None,
                "response_time": None,
                "is_available": False,
            }


async def monitor_loop():
    """
    Основной цикл мониторинга:
    периодически проверяет все сайты из базы.
    """
    while True:
        async with AsyncSessionLocal() as session:
            sites = await crud.list_sites(session)

            if not sites:
                logger.info("No sites to monitor")
            else:
                for site in sites:
                    await check_site(session, site)

        # Ждём перед следующим циклом
        await asyncio.sleep(settings.DEFAULT_INTERVAL)


async def start_monitor():
    """
    Запускает сервис мониторинга (бесконечный цикл).
    """
    logger.info("Starting monitor service")
    await monitor_loop()
