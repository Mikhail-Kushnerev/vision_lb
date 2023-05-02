"""Модуль исключений"""

from utils.constants import Answer
from utils.exceptions.base import ErrorBase


class WrongFormatError(ErrorBase):
    """Не поддерживаемое расширение объекта."""


def exc_handler(foo):
    """Метод обрабатывает исключения."""
    async def wrapper(*args, **kwargs):
        try:
            result = await foo(*args, **kwargs)
        except ErrorBase:
            return Answer.FAIL_PLOT
        else:
            return result

    return wrapper

