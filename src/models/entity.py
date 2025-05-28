"""Base entity class for all simulation objects."""

from abc import ABC, abstractmethod
from typing import Tuple, Optional
from ..utils import clamp_position, random_direction


# Display constants for different entity types
TILE_EMPTY = "⬛"
TILE_ANT = "🟠"
TILE_PLANT = "🌿"
TILE_FUNGUS = "🍄"
TILE_PARASITE = "🧫"
TILE_PREDATOR = "🐍"


class Entity(ABC):
    """Base class for all entities in the simulation."""
    
    def __init__(self, position: Tuple[int, int]):
        """Initialize entity with position.
        
        Args:
            position: (x, y) coordinates on the grid
        """
        self.position = position
        self.active = True
    
    @property
    def x(self) -> int:
        """Get x coordinate."""
        return self.position[0]
    
    @property
    def y(self) -> int:
        """Get y coordinate."""
        return self.position[1]
    
    def move_to(self, new_position: Tuple[int, int], grid_size: int) -> None:
        """Move entity to new position, clamping to grid bounds.
        
        Args:
            new_position: Target (x, y) coordinates
            grid_size: Size of the simulation grid
        """
        self.position = clamp_position(new_position, grid_size)
    
    def move_by(self, delta: Tuple[int, int], grid_size: int) -> None:
        """Move entity by relative offset.
        
        Args:
            delta: (dx, dy) offset to move by
            grid_size: Size of the simulation grid
        """
        new_x = self.x + delta[0]
        new_y = self.y + delta[1]
        self.move_to((new_x, new_y), grid_size)
    
    def random_move(self, grid_size: int) -> None:
        """Move entity in a random direction or stay in place."""
        direction = random_direction()
        self.move_by(direction, grid_size)
    
    def deactivate(self) -> None:
        """Mark entity as inactive (to be removed from simulation)."""
        self.active = False
    
    def is_at_position(self, position: Tuple[int, int]) -> bool:
        """Check if entity is at given position."""
        return self.position == position
    
    @abstractmethod
    def get_tile_symbol(self) -> str:
        """Get the display symbol for this entity type."""
        pass
    
    @abstractmethod
    def update(self, environment: 'Environment') -> None:
        """Update entity state for one simulation step.
        
        Args:
            environment: Reference to the simulation environment
        """
        pass
    
    def __repr__(self) -> str:
        """String representation of entity."""
        return f"{self.__class__.__name__}(position={self.position}, active={self.active})" 