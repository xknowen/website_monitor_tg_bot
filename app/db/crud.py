from sqlalchemy import select, delete
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Site, Check
from app.core.logger import get_logger

logger = get_logger()


async def create_site(session: AsyncSession, url: str, interval: int) -> Site:
    """
    Создаёт новый сайт или возвращает существующий при попытке дубликата.

    Args:
        session (AsyncSession): Сессия базы данных.
        url (str): Адрес сайта.
        interval (int): Интервал проверки в секундах.

    Returns:
        Site: Созданный или найденный сайт.
    """
    site = Site(url=url, interval=interval)
    session.add(site)
    try:
        await session.commit()
        await session.refresh(site)
        logger.info(f'Site added: {url}')
        return site
    except IntegrityError:
        await session.rollback()
        existing = (
            await session.execute(select(Site).where(Site.url == url))
        ).scalar_one()
        return existing


async def list_sites(session: AsyncSession) -> list[Site]:
    """
    Возвращает список всех сайтов.

    Args:
        session (AsyncSession): Сессия базы данных.

    Returns:
        list[Site]: Список сайтов.
    """
    result = await session.execute(select(Site))
    return result.scalars().all()


async def get_site(session: AsyncSession, site_id: int) -> Site | None:
    """
    Получает сайт по его ID.

    Args:
        session (AsyncSession): Сессия базы данных.
        site_id (int): Идентификатор сайта.

    Returns:
        Site | None: Найденный сайт или None.
    """
    result = await session.execute(select(Site).where(Site.id == site_id))
    return result.scalar_one_or_none()


async def delete_site(session: AsyncSession, site_id: int) -> None:
    """
    Удаляет сайт по ID.

    Args:
        session (AsyncSession): Сессия базы данных.
        site_id (int): Идентификатор сайта.
    """
    await session.execute(delete(Site).where(Site.id == site_id))
    await session.commit()
    logger.info(f'Site deleted: {site_id}')


async def create_check(
    session: AsyncSession,
    site: Site,
    status_code: int | None,
    response_time: float | None,
    is_available: bool,
) -> Check:
    """
    Добавляет запись о проверке сайта.

    Args:
        session (AsyncSession): Сессия базы данных.
        site (Site): Проверяемый сайт.
        status_code (int | None): Код ответа HTTP.
        response_time (float | None): Время ответа.
        is_available (bool): Флаг доступности.

    Returns:
        Check: Добавленная запись проверки.
    """
    check = Check(
        site_id=site.id,
        status_code=status_code,
        response_time=response_time,
        is_available=is_available,
    )
    session.add(check)
    await session.commit()
    await session.refresh(check)
    return check


async def last_checks(session: AsyncSession, site_id: int, limit: int = 10) -> list[Check]:
    """
    Возвращает последние проверки сайта.

    Args:
        session (AsyncSession): Сессия базы данных.
        site_id (int): Идентификатор сайта.
        limit (int): Ограничение на количество записей.

    Returns:
        list[Check]: Последние проверки.
    """
    result = await session.execute(
        select(Check)
        .where(Check.site_id == site_id)
        .order_by(Check.checked_at.desc())
        .limit(limit)
    )
    return result.scalars().all()


async def stats_for_site(session: AsyncSession, site_id: int) -> dict[str, float | None]:
    """
    Считает статистику по сайту: аптайм и среднее время отклика.

    Args:
        session (AsyncSession): Сессия базы данных.
        site_id (int): Идентификатор сайта.

    Returns:
        dict[str, float | None]: Статистика (uptime %, average_response).
    """
    checks = await last_checks(session, site_id, limit=1000)
    total = len(checks)
    if total == 0:
        return {"uptime": None, "average_response": None}

    up = sum(1 for c in checks if c.is_available)
    avg = sum((c.response_time or 0) for c in checks) / total

    return {"uptime": up / total * 100, "average_response": avg}
