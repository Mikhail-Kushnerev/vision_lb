"""Модуль содержит фабрики для предоставления CRUD-объектов."""

from .base import BaseCRUD
from .track import TrackCRUD


def get_crud_by_client(crud_name) -> BaseCRUD:
    crud = {
        'trackservice': TrackCRUD
    }
    return crud[crud_name.__name__.lower()]
