"""Predator entity implementation."""

from typing import Tuple, List, TYPE_CHECKING
from .entity import Entity, TILE_PREDATOR
from ..utils import manhattan_distance, probability_check

if TYPE_CHECKING:
    from ..environment import Environment


class Predator(Entity):
    """Represents a predator that hunts ants."""
    
    def __init__(self, position: Tuple[int, int], hunting_efficiency: float = 1.0):
        """Initialize predator at given position.
        
        Args:
            position: Starting (x, y) coordinates
            hunting_efficiency: How effective the predator is at hunting (0.5 to 2.0)
        """
        super().__init__(position)
        self.hunting_efficiency = hunting_efficiency
        self.energy = 100  # Predators need energy to survive
        self.max_energy = 150
        self.energy_decay_rate = 2  # Energy lost per step
        self.hunt_range = 3  # How far predator can sense ants
        self.last_meal_step = 0
    
    def get_tile_symbol(self) -> str:
        """Get the display symbol for predators."""
        return TILE_PREDATOR
    
    def update(self, environment: 'Environment') -> None:
        """Update predator state for one simulation step.
        
        Args:
            environment: Reference to the simulation environment
        """
        # Decay energy
        self.energy -= self.energy_decay_rate
        
        # Die if energy is too low
        if self.energy <= 0:
            self.deactivate()
            return
        
        # Hunt for ants
        self._hunt(environment)
        
        # Move towards prey or randomly if no prey found
        self._move(environment)
    
    def _hunt(self, environment: 'Environment') -> None:
        """Hunt for ants within range.
        
        Args:
            environment: Reference to the simulation environment
        """
        # Find ants within hunting range
        nearby_ants = self._find_nearby_ants(environment)
        
        if nearby_ants:
            # Attack the closest ant
            closest_ant = min(nearby_ants, 
                             key=lambda ant: manhattan_distance(self.position, ant.position))
            
            # Check if attack is successful
            attack_chance = 0.7 * self.hunting_efficiency
            if probability_check(attack_chance):
                closest_ant.deactivate()
                # Gain energy from successful hunt
                self.energy = min(self.max_energy, self.energy + 30)
                self.last_meal_step = 0
    
    def _find_nearby_ants(self, environment: 'Environment') -> List['Ant']:
        """Find ants within hunting range.
        
        Args:
            environment: Reference to the simulation environment
            
        Returns:
            List of ants within hunting range
        """
        nearby_ants = []
        for ant in environment.ants:
            if ant.active and manhattan_distance(self.position, ant.position) <= self.hunt_range:
                nearby_ants.append(ant)
        return nearby_ants
    
    def _move(self, environment: 'Environment') -> None:
        """Move predator, preferring to move towards prey.
        
        Args:
            environment: Reference to the simulation environment
        """
        # Find nearby ants to move towards
        nearby_ants = self._find_nearby_ants(environment)
        
        if nearby_ants:
            # Move towards the closest ant
            closest_ant = min(nearby_ants, 
                             key=lambda ant: manhattan_distance(self.position, ant.position))
            target_pos = closest_ant.position
            
            # Calculate direction towards target
            dx = 0 if target_pos[0] == self.x else (1 if target_pos[0] > self.x else -1)
            dy = 0 if target_pos[1] == self.y else (1 if target_pos[1] > self.y else -1)
            
            self.move_by((dx, dy), environment.grid_size)
        else:
            # No ants nearby, move randomly
            self.random_move(environment.grid_size)
    
    def is_starving(self) -> bool:
        """Check if predator is starving.
        
        Returns:
            True if predator has low energy
        """
        return self.energy < 30
    
    def get_threat_level(self) -> float:
        """Get the threat level of this predator.
        
        Returns:
            Threat level (0.0 to 2.0)
        """
        # Threat increases with hunting efficiency and decreases with low energy
        energy_factor = self.energy / self.max_energy
        return self.hunting_efficiency * energy_factor
    
    def __repr__(self) -> str:
        """String representation of predator."""
        return (f"Predator(position={self.position}, active={self.active}, "
                f"energy={self.energy}, hunting_efficiency={self.hunting_efficiency:.2f})") 