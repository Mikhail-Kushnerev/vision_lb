from .track import GraphCRUD


def get_crud_by_client(crud_name):
    crud = {
        'trackservice': GraphCRUD
    }
    return crud[crud_name.__name__.lower()]
