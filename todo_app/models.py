from dataclasses import dataclass, field
import itertools


_id_counter = itertools.count(1)


@dataclass
class TodoItem:
    """Entitas sederhana untuk satu item todo."""

    text: str
    completed: bool = False
    id: int = field(default_factory=lambda: next(_id_counter))

