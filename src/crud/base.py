class BaseCRUD:
    def __init__(self, model, client):
        self._model = model
        self._client = client

    async def get(self, obj_id, *args):
        pass

    async def create(self, points):
        pass
