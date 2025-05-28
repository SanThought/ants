"""Utility functions for the leafcutter colony simulation."""

import random
import math
from typing import Tuple, List, Iterator
from enum import Enum


class Direction(Enum):
    """Cardinal directions for movement."""
    NORTH = (-1, 0)
    SOUTH = (1, 0)
    WEST = (0, -1)
    EAST = (0, 1)
    STAY = (0, 0)


class Climate(Enum):
    """Climate states."""
    RAIN = "rain"
    DRY = "dry"


def manhattan_distance(pos1: Tuple[int, int], pos2: Tuple[int, int]) -> int:
    """Calculate Manhattan distance between two positions."""
    return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])


def euclidean_distance(pos1: Tuple[int, int], pos2: Tuple[int, int]) -> float:
    """Calculate Euclidean distance between two positions."""
    return math.sqrt((pos1[0] - pos2[0])**2 + (pos1[1] - pos2[1])**2)


def get_neighbors(position: Tuple[int, int], grid_size: int, 
                 include_diagonals: bool = False) -> List[Tuple[int, int]]:
    """Get all valid neighboring positions within grid bounds."""
    x, y = position
    neighbors = []
    
    # Cardinal directions
    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
    
    # Add diagonals if requested
    if include_diagonals:
        directions.extend([(-1, -1), (-1, 1), (1, -1), (1, 1)])
    
    for dx, dy in directions:
        nx, ny = x + dx, y + dy
        if 0 <= nx < grid_size and 0 <= ny < grid_size:
            neighbors.append((nx, ny))
    
    return neighbors


def get_positions_within_radius(center: Tuple[int, int], radius: int, 
                               grid_size: int) -> List[Tuple[int, int]]:
    """Get all positions within a given radius of center point."""
    positions = []
    x, y = center
    
    for dx in range(-radius, radius + 1):
        for dy in range(-radius, radius + 1):
            if manhattan_distance((0, 0), (dx, dy)) <= radius:
                nx, ny = x + dx, y + dy
                if 0 <= nx < grid_size and 0 <= ny < grid_size:
                    positions.append((nx, ny))
    
    return positions


def clamp_position(position: Tuple[int, int], grid_size: int) -> Tuple[int, int]:
    """Ensure position is within grid bounds."""
    x, y = position
    return (max(0, min(x, grid_size - 1)), max(0, min(y, grid_size - 1)))


def random_position(grid_size: int) -> Tuple[int, int]:
    """Generate a random position within grid bounds."""
    return (random.randint(0, grid_size - 1), random.randint(0, grid_size - 1))


def random_positions(count: int, grid_size: int) -> List[Tuple[int, int]]:
    """Generate multiple random positions within grid bounds."""
    return [random_position(grid_size) for _ in range(count)]


def random_direction() -> Tuple[int, int]:
    """Get a random movement direction including staying in place."""
    return random.choice(list(Direction)).value


def weighted_random_choice(items: List[any], weights: List[float]) -> any:
    """Choose random item based on weights."""
    if not items or not weights or len(items) != len(weights):
        raise ValueError("Items and weights must be non-empty and same length")
    
    total_weight = sum(weights)
    if total_weight <= 0:
        raise ValueError("Total weight must be positive")
    
    r = random.uniform(0, total_weight)
    cumulative = 0
    
    for item, weight in zip(items, weights):
        cumulative += weight
        if r <= cumulative:
            return item
    
    return items[-1]  # Fallback to last item


def probability_check(probability: float) -> bool:
    """Return True with given probability (0.0 to 1.0)."""
    return random.random() < probability


def seed_random(seed: int = None) -> None:
    """Set random seed for reproducible simulations."""
    random.seed(seed)


def circular_iterator(items: List[any]) -> Iterator[any]:
    """Create an iterator that cycles through items indefinitely."""
    while True:
        for item in items:
            yield item


def interpolate(start: float, end: float, factor: float) -> float:
    """Linear interpolation between start and end values."""
    factor = max(0.0, min(1.0, factor))  # Clamp factor to [0, 1]
    return start + (end - start) * factor 