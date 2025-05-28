"""Environment management for the leafcutter colony simulation."""

from typing import List, Tuple, Dict, Any
import random
from src.config import SimulationConfig
from src.models import (
    Entity, Ant, Plant, Fungus, Parasite, Predator,
    TILE_EMPTY, TILE_ANT, TILE_PLANT, TILE_FUNGUS, TILE_PARASITE, TILE_PREDATOR
)
from src.utils import random_positions, probability_check, Climate


class Environment:
    """Manages the simulation grid and all entities."""
    
    def __init__(self, config: SimulationConfig):
        """Initialize environment with given configuration.
        
        Args:
            config: Simulation configuration
        """
        self.config = config
        self.grid_size = config.grid_size
        self.step_count = 0
        
        # Entity collections
        self.ants: List[Ant] = []
        self.plants: List[Plant] = []
        self.fungi: List[Fungus] = []
        self.parasites: List[Parasite] = []
        self.predators: List[Predator] = []
        
        # Climate state
        self.current_climate = Climate.DRY
        self.climate_timer = 0
        
        # Colony resources
        self.food_stock = 0  # Total fungus nutrition available
        self.larvae_stock = 0  # Developing ants
        
        # Metrics tracking
        self.metrics: Dict[str, List[Any]] = {
            'step': [],
            'ant_count': [],
            'plant_count': [],
            'fungus_count': [],
            'parasite_count': [],
            'predator_count': [],
            'food_stock': [],
            'climate': []
        }
        
        self._initialize_entities()
    
    def _initialize_entities(self) -> None:
        """Initialize entities with random positions."""
        # Create ants
        ant_positions = random_positions(self.config.initial_ants, self.grid_size)
        self.ants = [Ant(pos) for pos in ant_positions]
        
        # Create plants
        plant_positions = random_positions(self.config.initial_plants, self.grid_size)
        self.plants = [Plant(pos) for pos in plant_positions]
        
        # Create fungi
        fungus_positions = random_positions(self.config.initial_fungi, self.grid_size)
        self.fungi = [Fungus(pos) for pos in fungus_positions]
        
        # Create parasites
        parasite_positions = random_positions(self.config.initial_parasites, self.grid_size)
        self.parasites = [Parasite(pos) for pos in parasite_positions]
        
        # Create predators
        predator_positions = random_positions(self.config.initial_predators, self.grid_size)
        self.predators = [Predator(pos) for pos in predator_positions]
    
    def step(self) -> None:
        """Advance simulation by one step."""
        self.step_count += 1
        
        # Update climate
        self._update_climate()
        
        # Update all entities
        self._update_entities()
        
        # Remove inactive entities
        self._cleanup_entities()
        
        # Environmental processes
        self._plant_regeneration()
        self._ant_reproduction()
        self._predator_spawning()
        
        # Update metrics
        self._update_metrics()
    
    def _update_climate(self) -> None:
        """Update climate state based on configuration."""
        self.climate_timer += 1
        
        if self.climate_timer >= self.config.climate.cycle_length:
            # Switch climate
            if self.current_climate == Climate.DRY:
                self.current_climate = Climate.RAIN
                self.climate_timer = 0
            else:
                self.current_climate = Climate.DRY
                self.climate_timer = 0
    
    def _update_entities(self) -> None:
        """Update all entities for one simulation step."""
        # Update in specific order to maintain consistent behavior
        for entity_list in [self.plants, self.fungi, self.parasites, self.predators, self.ants]:
            for entity in entity_list[:]:  # Copy list to avoid modification during iteration
                if entity.active:
                    entity.update(self)
    
    def _cleanup_entities(self) -> None:
        """Remove inactive entities from collections."""
        self.ants = [ant for ant in self.ants if ant.active]
        self.plants = [plant for plant in self.plants if plant.active]
        self.fungi = [fungus for fungus in self.fungi if fungus.active]
        self.parasites = [parasite for parasite in self.parasites if parasite.active]
        self.predators = [predator for predator in self.predators if predator.active]
    
    def _plant_regeneration(self) -> None:
        """Handle plant regeneration based on configuration and climate."""
        if self.step_count % self.config.plant_regeneration.interval != 0:
            return
        
        current_plant_count = len(self.plants)
        max_plants = self.config.plant_regeneration.max_plants
        
        if current_plant_count >= max_plants:
            return
        
        # Get base regeneration probability
        base_prob = self.config.plant_regeneration.probability
        
        # Apply climate modifiers
        if self.current_climate == Climate.RAIN:
            regen_prob = base_prob * self.config.climate.rain_effects.plant_regen_multiplier
        else:
            regen_prob = base_prob * self.config.climate.dry_effects.plant_regen_multiplier
        
        if probability_check(regen_prob):
            # Find empty positions for new plants
            occupied_positions = set()
            for entity_list in [self.ants, self.plants, self.fungi, self.parasites, self.predators]:
                for entity in entity_list:
                    occupied_positions.add(entity.position)
            
            # Generate random position that's not occupied
            attempts = 0
            while attempts < 20:  # Limit attempts to avoid infinite loop
                pos = (random.randint(0, self.grid_size - 1), 
                       random.randint(0, self.grid_size - 1))
                if pos not in occupied_positions:
                    self.plants.append(Plant(pos))
                    break
                attempts += 1
    
    def _ant_reproduction(self) -> None:
        """Handle ant reproduction based on food availability."""
        if self.step_count % self.config.reproduction.larvae_period != 0:
            return
        
        # Calculate available food
        total_nutrition = sum(fungus.nutrition_value for fungus in self.fungi if fungus.can_be_consumed())
        
        if total_nutrition >= self.config.reproduction.food_threshold:
            # Consume food for reproduction
            food_needed = self.config.reproduction.food_threshold
            for fungus in self.fungi[:]:
                if food_needed <= 0:
                    break
                if fungus.can_be_consumed():
                    consumed = min(food_needed, fungus.nutrition_value)
                    food_needed -= consumed
                    if consumed >= fungus.nutrition_value:
                        fungus.deactivate()
                    else:
                        fungus.nutrition_value -= consumed
            
            # Add new ants
            new_ant_count = self.config.reproduction.larvae_per_cycle
            for _ in range(new_ant_count):
                # Place new ants near existing ants if possible
                if self.ants:
                    parent = random.choice(self.ants)
                    # Try to place near parent
                    from src.utils import get_neighbors
                    possible_positions = get_neighbors(parent.position, self.grid_size)
                    possible_positions.append(parent.position)  # Can be at same position
                    
                    # Filter out occupied positions
                    occupied = set()
                    for entity_list in [self.plants, self.fungi, self.parasites, self.predators]:
                        for entity in entity_list:
                            occupied.add(entity.position)
                    
                    available_positions = [pos for pos in possible_positions if pos not in occupied]
                    
                    if available_positions:
                        new_pos = random.choice(available_positions)
                    else:
                        new_pos = (random.randint(0, self.grid_size - 1), 
                                  random.randint(0, self.grid_size - 1))
                else:
                    new_pos = (random.randint(0, self.grid_size - 1), 
                              random.randint(0, self.grid_size - 1))
                
                self.ants.append(Ant(new_pos))
    
    def _predator_spawning(self) -> None:
        """Handle dynamic predator spawning based on ant population."""
        current_ants = len(self.ants)
        current_predators = len(self.predators)
        
        if current_ants == 0:
            return  # No ants, no need for predators
        
        # Calculate target predator count
        target_ratio = self.config.predator_balance.target_ant_predator_ratio
        target_predators = max(1, current_ants // target_ratio)
        
        # Adjust spawn probability based on current ratio
        base_spawn_chance = self.config.predator_balance.base_spawn_chance
        
        if current_predators < target_predators:
            # Need more predators
            spawn_multiplier = 1.5
        elif current_predators > target_predators:
            # Too many predators
            spawn_multiplier = 0.3
        else:
            # Balanced
            spawn_multiplier = 1.0
        
        # Apply climate effects
        if self.current_climate == Climate.RAIN:
            spawn_multiplier *= self.config.climate.rain_effects.predator_spawn_reduction
        else:
            spawn_multiplier *= self.config.climate.dry_effects.predator_spawn_increase
        
        final_spawn_chance = base_spawn_chance * spawn_multiplier
        
        if probability_check(final_spawn_chance):
            pos = (random.randint(0, self.grid_size - 1), 
                   random.randint(0, self.grid_size - 1))
            self.predators.append(Predator(pos))
    
    def _update_metrics(self) -> None:
        """Update metrics for tracking simulation state."""
        self.metrics['step'].append(self.step_count)
        self.metrics['ant_count'].append(len(self.ants))
        self.metrics['plant_count'].append(len(self.plants))
        self.metrics['fungus_count'].append(len(self.fungi))
        self.metrics['parasite_count'].append(len(self.parasites))
        self.metrics['predator_count'].append(len(self.predators))
        self.metrics['food_stock'].append(sum(f.nutrition_value for f in self.fungi))
        self.metrics['climate'].append(self.current_climate.value)
    
    def render_grid(self) -> str:
        """Render the current state as a grid string.
        
        Returns:
            String representation of the grid
        """
        # Initialize grid with empty tiles
        grid = [[TILE_EMPTY for _ in range(self.grid_size)] for _ in range(self.grid_size)]
        
        # Place entities on grid (order matters for overlapping)
        entity_layers = [
            (self.plants, TILE_PLANT),
            (self.fungi, TILE_FUNGUS),
            (self.parasites, TILE_PARASITE),
            (self.predators, TILE_PREDATOR),
            (self.ants, TILE_ANT)  # Ants on top
        ]
        
        for entity_list, tile_symbol in entity_layers:
            for entity in entity_list:
                if entity.active:
                    grid[entity.x][entity.y] = tile_symbol
        
        # Convert grid to string
        return "\n".join("".join(row) for row in grid)
    
    def add_ant(self, position: Tuple[int, int]) -> None:
        """Add a new ant at the specified position."""
        self.ants.append(Ant(position))
    
    def add_plant(self, position: Tuple[int, int]) -> None:
        """Add a new plant at the specified position."""
        self.plants.append(Plant(position))
    
    def add_fungus(self, position: Tuple[int, int]) -> None:
        """Add a new fungus at the specified position."""
        self.fungi.append(Fungus(position))
    
    def add_parasite(self, position: Tuple[int, int], virulence: float = 1.0) -> None:
        """Add a new parasite at the specified position."""
        self.parasites.append(Parasite(position, virulence))
    
    def add_predator(self, position: Tuple[int, int]) -> None:
        """Add a new predator at the specified position."""
        self.predators.append(Predator(position))
    
    def get_entity_counts(self) -> Dict[str, int]:
        """Get count of each entity type.
        
        Returns:
            Dictionary with entity counts
        """
        return {
            'ants': len(self.ants),
            'plants': len(self.plants),
            'fungi': len(self.fungi),
            'parasites': len(self.parasites),
            'predators': len(self.predators)
        } 