"""Fungus entity implementation."""

from typing import Tuple, TYPE_CHECKING
from .entity import Entity, TILE_FUNGUS
import random

if TYPE_CHECKING:
    from ..environment import Environment


class Fungus(Entity):
    """Represents a fungus food source grown from harvested plants."""
    
    def __init__(self, position: Tuple[int, int], nutrition_value: float = 10.0):
        """Initialize fungus at given position.
        
        Args:
            position: Starting (x, y) coordinates
            nutrition_value: Nutritional value of this fungus
        """
        super().__init__(position)
        self.nutrition_value = nutrition_value
        self.age = 0  # How long the fungus has existed
        self.max_age = 100  # Fungi eventually decay
        self.health = 1.0  # Full health initially
    
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
        
        # Suppress nearby parasites based on fungus health
        if self.health > 0.4:  # Only healthy fungi can suppress parasites
            nearby_parasites = environment.get_nearby_entities(self.position, entity_type='parasite', radius=2)
            for parasite in nearby_parasites:
                # Stronger fungi are better at suppressing parasites
                suppression_chance = self.health * 0.3  # 30% max chance per update
                if random.random() < suppression_chance:
                    parasite.active = False  # Remove the parasite
    
    def can_be_consumed(self) -> bool:
        """Check if fungus can be consumed by ants.
        
        Returns:
            True if fungus is ready to be consumed
        """
        return self.nutrition_value > 5  # Minimum nutrition threshold
    
    def consume(self, amount: float) -> float:
        """Consume some nutrition from the fungus."""
        consumed = min(amount, self.nutrition_value)
        self.nutrition_value -= consumed
        self.health = max(0.2, self.nutrition_value / 10.0)  # Health reflects nutrition
        return consumed
    
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