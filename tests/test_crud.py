import pytest
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from app.db.database import Base
from app.db import crud

# Тестовая база данных (SQLite в памяти/файле)
DATABASE_URL = "sqlite+aiosqlite:///./test_site_monitor.db"


@pytest.fixture(scope="module")
async def setup_db():
    """
    Инициализация тестовой БД.

    - Создаёт движок SQLite
    - Дропает и пересоздаёт таблицы
    - Возвращает фабрику асинхронных сессий
    """
    engine = create_async_engine(DATABASE_URL, future=True)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    AsyncSessionLocal = sessionmaker(
        engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    yield AsyncSessionLocal

    # Завершаем работу движка после тестов
    await engine.dispose()


@pytest.mark.asyncio
async def test_create_and_list(setup_db):
    """
    Проверяет создание сайта и его отображение в списке.
    """
    AsyncSessionLocal = setup_db
    async with AsyncSessionLocal() as session:
        site = await crud.create_site(session, "http://example.com", 30)
        assert site.id is not None

        sites = await crud.list_sites(session)
        assert len(sites) == 1


@pytest.mark.asyncio
async def test_delete(setup_db):
    """
    Проверяет удаление сайта из БД.
    """
    AsyncSessionLocal = setup_db
    async with AsyncSessionLocal() as session:
        sites = await crud.list_sites(session)
        assert len(sites) == 1

        await crud.delete_site(session, sites[0].id)

        sites2 = await crud.list_sites(session)
        assert len(sites2) == 0
