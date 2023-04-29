from utils.graph import GraphParams


class PreparationGraph:
    def __init__(self, params):
        self._param = params

    def prepare(self):
        graph_id = self._param.get('graph_id')
        points_x, points_y, = self._param.get('points_X'), self._param.get('points_Y')
        for x, y in zip(points_x, points_y):
            point = GraphParams(graph_id, x, y)
            yield point.to_dict()
