from dataclasses import dataclass

@dataclass(slots=True)
class Vector2i:
    x: int = 0
    y: int = 0
    