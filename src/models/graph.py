from uuid import uuid4

from sqlalchemy import Column, Float
from sqlalchemy.dialects.postgresql import UUID

from config.db import Base


class PointsModel(Base):
    graph_id = Column(UUID(as_uuid=True), default=uuid4, nullable=False)
    points_X = Column(Float)
    points_Y = Column(Float)
