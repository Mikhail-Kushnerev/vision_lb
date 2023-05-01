from .track import TrackCRUD


def get_crud_by_client(crud_name):
    crud = {
        'trackservice': TrackCRUD
    }
    return crud[crud_name.__name__.lower()]
