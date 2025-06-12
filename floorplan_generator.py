import random
from dataclasses import dataclass
from typing import List

@dataclass
class Room:
    x: int
    y: int
    width: int
    height: int

@dataclass
class FloorPlan:
    rooms: List[Room]


def generate_random_plan(num_rooms: int = 4) -> FloorPlan:
    """Generate a simple random floor plan."""
    rooms = []
    x_offset = 0
    for _ in range(num_rooms):
        width = random.randint(3, 8)
        height = random.randint(3, 8)
        rooms.append(Room(x=x_offset, y=0, width=width, height=height))
        x_offset += width
    return FloorPlan(rooms=rooms)
