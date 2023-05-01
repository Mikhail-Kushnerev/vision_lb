"""Базовая Pydantic-схема для классов наследников."""

import orjson
from pydantic import BaseModel


def orjson_dumps(obj, *, default):
    """
    Метод ускоряет работу с JSON

    Args:
        obj (Any): Объект для представления в словарь
        default (Callable): Функция для сериализации.

    Returns: unicode

    """
    return orjson.dumps(obj, default=default).decode()


class BaseSchema(BaseModel):
    """Класс базовой Pydantic-схемы."""

    class Config:
        orm_mode = True
        json_loads = orjson.loads
        json_dumps = orjson_dumps
