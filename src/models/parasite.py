"""Parasite entity implementation."""

from typing import Tuple, TYPE_CHECKING
from .entity import Entity, TILE_PARASITE
from ..utils import probability_check

if TYPE_CHECKING:
    from ..environment import Environment


class Parasite(Entity):
    """Represents a parasite that threatens ants."""
    
    def __init__(self, position: Tuple[int, int], virulence: float = 1.0):
        """Initialize parasite at given position.
        
        Args:
            position: Starting (x, y) coordinates
            virulence: How deadly the parasite is (0.0 to 2.0)
        """
        super().__init__(position)
        self.virulence = virulence
        self.age = 0
        self.max_age = 200  # Parasites persist longer than fungi
        self.spread_attempts = 0
        self.max_spread_attempts = 5  # Limit spreading to prevent explosion
    
    def get_tile_symbol(self) -> str:
        """Get the display symbol for parasites."""
        return TILE_PARASITE
    
    def update(self, environment: 'Environment') -> None:
        """Update parasite state for one simulation step.
        
        Args:
            environment: Reference to the simulation environment
        """
        # Age the parasite
        self.age += 1
        
        # Die of old age
        if self.age >= self.max_age:
            self.deactivate()
            return
        
        # Attempt to spread to nearby locations
        self._attempt_spread(environment)
        
        # Virulence may decrease over time
        if self.age > 50:
            self.virulence = max(0.1, self.virulence * 0.99)
    
    def _attempt_spread(self, environment: 'Environment') -> None:
        """Attempt to spread parasite to nearby locations.
        
        Args:
            environment: Reference to the simulation environment
        """
        if self.spread_attempts >= self.max_spread_attempts:
            return
        
        # Get spread chance from configuration
        spread_chance = environment.config.parasite_dynamics.spread_chance
        
        # Adjust spread chance based on virulence
        adjusted_chance = spread_chance * self.virulence
        
        if probability_check(adjusted_chance):
            # Try to spread to a nearby location
            from ..utils import get_neighbors
            neighbors = get_neighbors(self.position, environment.grid_size)
            
            if neighbors:
                # Choose a random neighbor that doesn't already have a parasite
                import random
                available_neighbors = [
                    pos for pos in neighbors 
                    if not any(parasite.is_at_position(pos) for parasite in environment.parasites)
                ]
                
                if available_neighbors:
                    new_position = random.choice(available_neighbors)
                    # Create new parasite with reduced virulence
                    new_virulence = max(0.3, self.virulence * 0.8)
                    environment.add_parasite(new_position, new_virulence)
                    self.spread_attempts += 1
    
    def affects_ant(self, ant_position: Tuple[int, int]) -> bool:
        """Check if parasite affects an ant at given position.
        
        Args:
            ant_position: Position of the ant to check
            
        Returns:
            True if parasite affects the ant
        """
        # Parasites affect ants at the same position
        if self.position == ant_position:
            return True
        
        # Check if ant is within infection radius
        from ..utils import manhattan_distance
        infection_radius = 1  # Could be made configurable
        return manhattan_distance(self.position, ant_position) <= infection_radius
    
    def get_lethality(self) -> float:
        """Get the probability that this parasite kills an affected ant.
        
        Returns:
            Probability of killing an ant (0.0 to 1.0)
        """
        # Base lethality increases with virulence but caps at 0.8
        return min(0.8, 0.5 * self.virulence)
    
    def __repr__(self) -> str:
        """String representation of parasite."""
        return (f"Parasite(position={self.position}, active={self.active}, "
                f"virulence={self.virulence:.2f}, age={self.age})") 