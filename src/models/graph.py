from uuid import uuid4

from sqlalchemy import Column, Float
from sqlalchemy.dialects.postgresql import UUID

from config.db import Base


class PointsModel(Base):
    graph_id = Column(UUID(as_uuid=True), default=uuid4, nullable=False)
    point_X = Column(Float)
    point_Y = Column(Float)
