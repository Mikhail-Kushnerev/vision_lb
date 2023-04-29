from .base import BaseCRUD
from models import PointsModel


class GraphCRUD(BaseCRUD):
    pass


grap_crud = GraphCRUD(PointsModel)
