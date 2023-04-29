from dataclasses import dataclass, asdict
from uuid import UUID


@dataclass
class GraphParams:
    graph_id: UUID
    point_X: float
    point_Y: float

    def to_dict(self):
        return asdict(self)
