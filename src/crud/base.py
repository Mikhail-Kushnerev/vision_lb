"""Модуль базового CRUD."""


class BaseCRUD:
    """Класс базового CRUD"""
    def __init__(self, model, client):
        """Метод инициализирует модель БД и сессию подключения к БД"""
        self._model = model
        self._client = client

    async def get(self, obj_id, *args):
        """Метод описывает операцию READ"""
        pass

    async def create(self, points):
        """Метод описывает операцию CREATE"""
        pass
