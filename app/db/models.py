from sqlalchemy import Column, Integer, String, Boolean, DateTime, Float, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime

from app.db.database import Base


class Site(Base):
    """
    Модель для хранения информации о сайте.

    Атрибуты:
        id (int): Уникальный идентификатор сайта.
        url (str): URL сайта (уникальный, обязательный).
        interval (int): Интервал проверки сайта в секундах (по умолчанию 60).
        is_active (bool): Флаг активности сайта.
        checks (list[Check]): Связанные проверки сайта.
    """
    __tablename__ = "sites"

    id = Column(Integer, primary_key=True, index=True)
    url = Column(String, unique=True, nullable=False)
    interval = Column(Integer, default=60)
    is_active = Column(Boolean, default=True)

    # Связь с таблицей checks, каскадное удаление
    checks = relationship("Check", back_populates="site", cascade="all, delete-orphan")


class Check(Base):
    """
    Модель для хранения результатов проверок сайта.

    Атрибуты:
        id (int): Уникальный идентификатор проверки.
        site_id (int): Внешний ключ на таблицу sites.
        status_code (int): HTTP-код ответа (может быть None при ошибке).
        response_time (float): Время ответа сервера в секундах.
        is_available (bool): Доступность сайта.
        checked_at (datetime): Дата и время проверки.
        site (Site): Связанный объект сайта.
    """
    __tablename__ = "checks"

    id = Column(Integer, primary_key=True, index=True)
    site_id = Column(Integer, ForeignKey("sites.id"))
    status_code = Column(Integer, nullable=True)
    response_time = Column(Float, nullable=True)
    is_available = Column(Boolean, default=False)
    checked_at = Column(DateTime, default=datetime.now)

    # Обратная связь с Site
    site = relationship("Site", back_populates="checks")

