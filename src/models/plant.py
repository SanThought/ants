"""Plant entity implementation."""

from typing import Tuple, TYPE_CHECKING
from .entity import Entity, TILE_PLANT

if TYPE_CHECKING:
    from ..environment import Environment


class Plant(Entity):
    """Represents a plant/leaf that ants can harvest."""
    
    def __init__(self, position: Tuple[int, int], maturity: int = 100):
        """Initialize plant at given position.
        
        Args:
            position: Starting (x, y) coordinates
            maturity: Plant maturity level (affects harvest value)
        """
        super().__init__(position)
        self.maturity = maturity
        self.growth_rate = 1  # How fast the plant grows
    
    def get_tile_symbol(self) -> str:
        """Get the display symbol for plants."""
        return TILE_PLANT
    
    def update(self, environment: 'Environment') -> None:
        """Update plant state for one simulation step.
        
        Plants are mostly passive but can grow over time.
        
        Args:
            environment: Reference to the simulation environment
        """
        # Plants can grow if they haven't reached full maturity
        if self.maturity < 100:
            self.maturity = min(100, self.maturity + self.growth_rate)
    
    def can_be_harvested(self) -> bool:
        """Check if plant is mature enough to be harvested.
        
        Returns:
            True if plant can be harvested, False otherwise
        """
        return self.maturity >= 50  # Require at least 50% maturity
    
    def get_harvest_value(self) -> int:
        """Get the nutritional value of harvesting this plant.
        
        Returns:
            Harvest value based on maturity
        """
        return int(self.maturity * 0.01 * 10)  # Scale maturity to 0-10 range
    
    def __repr__(self) -> str:
        """String representation of plant."""
        return (f"Plant(position={self.position}, active={self.active}, "
                f"maturity={self.maturity})") 