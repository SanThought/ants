"""Fungus entity implementation."""

from typing import Tuple, TYPE_CHECKING
from .entity import Entity, TILE_FUNGUS

if TYPE_CHECKING:
    from ..environment import Environment


class Fungus(Entity):
    """Represents a fungus food source grown from harvested plants."""
    
    def __init__(self, position: Tuple[int, int], nutrition_value: int = 10):
        """Initialize fungus at given position.
        
        Args:
            position: Starting (x, y) coordinates
            nutrition_value: Nutritional value of this fungus
        """
        super().__init__(position)
        self.nutrition_value = nutrition_value
        self.age = 0  # How long the fungus has existed
        self.max_age = 100  # Fungi eventually decay
    
    def get_tile_symbol(self) -> str:
        """Get the display symbol for fungi."""
        return TILE_FUNGUS
    
    def update(self, environment: 'Environment') -> None:
        """Update fungus state for one simulation step.
        
        Args:
            environment: Reference to the simulation environment
        """
        # Age the fungus
        self.age += 1
        
        # Decay if too old
        if self.age >= self.max_age:
            self.deactivate()
            return
        
        # Fungi might slowly grow in nutrition value when young
        if self.age < 20 and self.nutrition_value < 20:
            self.nutrition_value += 0.1
    
    def can_be_consumed(self) -> bool:
        """Check if fungus can be consumed by ants.
        
        Returns:
            True if fungus is ready to be consumed
        """
        return self.nutrition_value > 5  # Minimum nutrition threshold
    
    def consume(self) -> int:
        """Consume the fungus and return its nutritional value.
        
        Returns:
            Nutritional value of the consumed fungus
        """
        value = self.nutrition_value
        self.deactivate()
        return value
    
    def is_spoiled(self) -> bool:
        """Check if fungus has spoiled due to age.
        
        Returns:
            True if fungus is too old to be useful
        """
        return self.age >= self.max_age * 0.8  # Spoils at 80% of max age
    
    def __repr__(self) -> str:
        """String representation of fungus."""
        return (f"Fungus(position={self.position}, active={self.active}, "
                f"nutrition_value={self.nutrition_value:.1f}, age={self.age})") 