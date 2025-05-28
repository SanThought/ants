"""Main simulation engine for the leafcutter colony simulation."""

from typing import Iterator, Optional, Dict, Any
import time
from src.config import SimulationConfig
from src.environment import Environment


class Simulation:
    """Main simulation engine that orchestrates the entire simulation."""
    
    def __init__(self, config: SimulationConfig):
        """Initialize simulation with configuration.
        
        Args:
            config: Simulation configuration
        """
        self.config = config
        self.environment = Environment(config)
        self.is_running = False
        self.current_step = 0
    
    def run(self, max_steps: Optional[int] = None) -> Iterator[str]:
        """Run the simulation and yield grid states.
        
        Args:
            max_steps: Maximum number of steps to run (uses config if None)
            
        Yields:
            Grid state as string for each simulation step
        """
        if max_steps is None:
            max_steps = self.config.simulation_steps
        
        self.is_running = True
        self.current_step = 0
        
        # Yield initial state
        yield self.environment.render_grid()
        
        while self.is_running and self.current_step < max_steps:
            # Check for extinction conditions
            if self._check_extinction():
                break
            
            # Advance simulation by one step
            self.environment.step()
            self.current_step += 1
            
            # Yield current state
            yield self.environment.render_grid()
    
    def run_with_delay(self, max_steps: Optional[int] = None) -> Iterator[str]:
        """Run simulation with built-in delay between steps.
        
        Args:
            max_steps: Maximum number of steps to run (uses config if None)
            
        Yields:
            Grid state as string for each simulation step
        """
        for grid_state in self.run(max_steps):
            yield grid_state
            if self.current_step > 0:  # Don't delay on initial state
                time.sleep(self.config.animation_speed)
    
    def step_once(self) -> str:
        """Advance simulation by exactly one step.
        
        Returns:
            Current grid state as string
        """
        if not self.is_running:
            self.is_running = True
        
        if self.current_step < self.config.simulation_steps and not self._check_extinction():
            self.environment.step()
            self.current_step += 1
        
        return self.environment.render_grid()
    
    def reset(self) -> None:
        """Reset simulation to initial state."""
        self.environment = Environment(self.config)
        self.is_running = False
        self.current_step = 0
    
    def stop(self) -> None:
        """Stop the simulation."""
        self.is_running = False
    
    def _check_extinction(self) -> bool:
        """Check if simulation should end due to extinction.
        
        Returns:
            True if simulation should end
        """
        # End if no ants remain
        if len(self.environment.ants) == 0:
            return True
        
        # End if ecosystem is completely barren
        total_entities = (len(self.environment.ants) + 
                         len(self.environment.plants) + 
                         len(self.environment.fungi))
        if total_entities < 3:  # Minimum viable ecosystem
            return True
        
        return False
    
    def get_status(self) -> Dict[str, Any]:
        """Get current simulation status.
        
        Returns:
            Dictionary with simulation status information
        """
        entity_counts = self.environment.get_entity_counts()
        
        return {
            'step': self.current_step,
            'max_steps': self.config.simulation_steps,
            'is_running': self.is_running,
            'climate': self.environment.current_climate.value,
            'climate_timer': self.environment.climate_timer,
            'entity_counts': entity_counts,
            'total_food': sum(f.nutrition_value for f in self.environment.fungi),
            'extinction_risk': self._calculate_extinction_risk(),
            'progress_percent': (self.current_step / self.config.simulation_steps) * 100
        }
    
    def _calculate_extinction_risk(self) -> str:
        """Calculate extinction risk level.
        
        Returns:
            Risk level as string: 'Low', 'Medium', 'High', 'Critical'
        """
        ant_count = len(self.environment.ants)
        food_count = len(self.environment.fungi)
        predator_count = len(self.environment.predators)
        
        if ant_count == 0:
            return 'Extinct'
        elif ant_count <= 3:
            return 'Critical'
        elif ant_count <= 10 or (predator_count > ant_count // 2):
            return 'High'
        elif food_count == 0 and len(self.environment.plants) == 0:
            return 'High'
        elif ant_count <= 20:
            return 'Medium'
        else:
            return 'Low'
    
    def get_metrics(self) -> Dict[str, list]:
        """Get simulation metrics for analysis.
        
        Returns:
            Dictionary containing metrics data
        """
        return self.environment.metrics.copy()
    
    def export_metrics_summary(self) -> Dict[str, Any]:
        """Export a summary of simulation metrics.
        
        Returns:
            Dictionary with statistical summary of metrics
        """
        metrics = self.environment.metrics
        
        if not metrics['step']:
            return {'error': 'No metrics available'}
        
        summary = {
            'total_steps': len(metrics['step']),
            'final_counts': {
                'ants': metrics['ant_count'][-1] if metrics['ant_count'] else 0,
                'plants': metrics['plant_count'][-1] if metrics['plant_count'] else 0,
                'fungi': metrics['fungus_count'][-1] if metrics['fungus_count'] else 0,
                'parasites': metrics['parasite_count'][-1] if metrics['parasite_count'] else 0,
                'predators': metrics['predator_count'][-1] if metrics['predator_count'] else 0,
            },
            'peak_counts': {
                'ants': max(metrics['ant_count']) if metrics['ant_count'] else 0,
                'plants': max(metrics['plant_count']) if metrics['plant_count'] else 0,
                'fungi': max(metrics['fungus_count']) if metrics['fungus_count'] else 0,
                'parasites': max(metrics['parasite_count']) if metrics['parasite_count'] else 0,
                'predators': max(metrics['predator_count']) if metrics['predator_count'] else 0,
            },
            'average_counts': {
                'ants': sum(metrics['ant_count']) / len(metrics['ant_count']) if metrics['ant_count'] else 0,
                'plants': sum(metrics['plant_count']) / len(metrics['plant_count']) if metrics['plant_count'] else 0,
                'fungi': sum(metrics['fungus_count']) / len(metrics['fungus_count']) if metrics['fungus_count'] else 0,
                'parasites': sum(metrics['parasite_count']) / len(metrics['parasite_count']) if metrics['parasite_count'] else 0,
                'predators': sum(metrics['predator_count']) / len(metrics['predator_count']) if metrics['predator_count'] else 0,
            },
            'colony_survived': metrics['ant_count'][-1] > 0 if metrics['ant_count'] else False,
            'steps_survived': len(metrics['step']),
            'max_food_stock': max(metrics['food_stock']) if metrics['food_stock'] else 0
        }
        
        return summary 