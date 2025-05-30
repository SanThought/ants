"""Ant entity implementation."""

from typing import Tuple, TYPE_CHECKING
from .entity import Entity, TILE_ANT

if TYPE_CHECKING:
    from ..environment import Environment


class Ant(Entity):
    """Represents a worker ant in the simulation."""
    
    def __init__(self, position: Tuple[int, int]):
        """Initialize ant at given position.
        
        Args:
            position: Starting (x, y) coordinates
        """
        super().__init__(position)
        self.energy = 100  # Energy level for future use
        self.carrying_food = False  # Whether ant is carrying food
    
    def get_tile_symbol(self) -> str:
        """Get the display symbol for ants."""
        return TILE_ANT
    
    def update(self, environment: 'Environment') -> None:
        """Update ant behavior for one simulation step.
        
        Args:
            environment: Reference to the simulation environment
        """
        # Check for threats at current position
        if self._check_for_threats(environment):
            self.deactivate()
            return
        
        # Move randomly
        self.random_move(environment.grid_size)
        
        # Check for threats at new position
        if self._check_for_threats(environment):
            self.deactivate()
            return
        
        # Interact with environment at new position
        self._interact_with_environment(environment)
    
    def _check_for_threats(self, environment: 'Environment') -> bool:
        """Check if ant is threatened by parasites or predators.
        
        Args:
            environment: Reference to the simulation environment
            
        Returns:
            True if ant should be eliminated, False otherwise
        """
        # Check for predators at this position
        for predator in environment.predators:
            if predator.is_at_position(self.position):
                return True
        
        # Check for parasites at this position
        for parasite in environment.parasites:
            if parasite.is_at_position(self.position):
                return True
        
        return False
    
    def _interact_with_environment(self, environment: 'Environment') -> None:
        """Interact with plants and fungi at current position.
        
        Args:
            environment: Reference to the simulation environment
        """
        # Check for plants to harvest
        plants_here = [plant for plant in environment.plants 
                      if plant.is_at_position(self.position)]
        
        if plants_here:
            # Remove the plant and create a fungus
            plant = plants_here[0]
            plant.deactivate()
            environment.add_fungus(self.position)
    
    def consume_fungus(self, fungus) -> float:
        """Consume nutrition from a fungus garden.
        
        Args:
            fungus: The fungus to consume from
            
        Returns:
            Amount of nutrition consumed
        """
        if fungus.can_be_consumed():
            consumed = fungus.consume(5.0)  # Consume up to 5 units of nutrition
            self.energy += consumed
            return consumed
        return 0.0
    
    def __repr__(self) -> str:
        """String representation of ant."""
        return (f"Ant(position={self.position}, active={self.active}, "
                f"energy={self.energy}, carrying_food={self.carrying_food})") 