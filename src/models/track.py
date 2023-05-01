"""Модуль описания БД трэка."""

from uuid import uuid4

from sqlalchemy import Column, Float
from sqlalchemy.dialects.postgresql import UUID

from config.db import Base


class PointsModel(Base):
    """Класс описывает поля БД `PointsModel`."""
    track_id = Column(UUID(as_uuid=True), default=uuid4, nullable=False)
    point_X = Column(Float, unique=False, nullable=False)
    point_Y = Column(Float, unique=False, nullable=False)
