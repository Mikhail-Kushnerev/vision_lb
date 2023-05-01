"""Модуль базового CRUD."""


class BaseCRUD:
    """Класс базового CRUD"""

    __slots__ = ('_model', '_client')

    def __init__(self, model, client):
        """Метод инициализирует модель БД и сессию подключения к БД"""
        self._model = model
        self._client = client

    async def get(self, *args):
        """Метод описывает операцию READ"""
        pass

    async def create(self, *args):
        """Метод описывает операцию CREATE"""
        pass
