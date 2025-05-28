"""Ecological balance functions for maintaining optimal simulation dynamics."""

from typing import Dict, Tuple
import math
from .config import SimulationConfig


class EcosystemBalance:
    """Manages ecological balance to prevent extinction and maintain interesting dynamics."""
    
    def __init__(self, config: SimulationConfig):
        """Initialize balance manager with configuration.
        
        Args:
            config: Simulation configuration
        """
        self.config = config
        self.balance_history = []
        self.intervention_count = 0
    
    def analyze_ecosystem_health(self, environment) -> Dict[str, float]:
        """Analyze the current health of the ecosystem.
        
        Args:
            environment: Current environment state
            
        Returns:
            Dictionary with health metrics (0.0 = critical, 1.0 = optimal)
        """
        ant_count = len(environment.ants)
        plant_count = len(environment.plants)
        fungus_count = len(environment.fungi)
        parasite_count = len(environment.parasites)
        predator_count = len(environment.predators)
        
        # Calculate individual component health
        population_health = self._calculate_population_health(ant_count)
        food_health = self._calculate_food_health(plant_count, fungus_count)
        predator_health = self._calculate_predator_balance(ant_count, predator_count)
        parasite_health = self._calculate_parasite_impact(ant_count, parasite_count)
        diversity_health = self._calculate_diversity_health(
            ant_count, plant_count, fungus_count, parasite_count, predator_count
        )
        
        return {
            'population': population_health,
            'food': food_health,
            'predator_balance': predator_health,
            'parasite_impact': parasite_health,
            'diversity': diversity_health,
            'overall': (population_health + food_health + predator_health + 
                       parasite_health + diversity_health) / 5.0
        }
    
    def calculate_sustainability_score(self, environment) -> Tuple[float, str]:
        """Calculate overall sustainability score and provide assessment.
        
        Args:
            environment: Current environment state
            
        Returns:
            Tuple of (sustainability score, text assessment)
        """
        health_metrics = self.analyze_ecosystem_health(environment)
        overall_health = health_metrics['overall']
        
        # Calculate sustainability based on health and stability
        ant_count = len(environment.ants)
        food_sources = len(environment.plants) + len(environment.fungi)
        predator_ratio = len(environment.predators) / max(1, ant_count)
        
        # Sustainability factors
        population_stable = ant_count >= 10
        food_sufficient = food_sources >= ant_count * 0.5
        predator_balanced = 0.05 <= predator_ratio <= 0.2
        
        # Calculate final score
        sustainability_score = overall_health * (
            (1.0 if population_stable else 0.6) *
            (1.0 if food_sufficient else 0.7) *
            (1.0 if predator_balanced else 0.8)
        )
        
        # Generate assessment
        if sustainability_score >= 0.8:
            assessment = "Thriving: The ecosystem is well-balanced and sustainable"
        elif sustainability_score >= 0.6:
            assessment = "Stable: The ecosystem is maintaining equilibrium"
        elif sustainability_score >= 0.4:
            assessment = "Vulnerable: The ecosystem shows signs of instability"
        elif sustainability_score >= 0.2:
            assessment = "At Risk: The ecosystem is struggling to maintain balance"
        else:
            assessment = "Critical: The ecosystem is approaching collapse"
        
        return sustainability_score, assessment
    
    def _calculate_population_health(self, ant_count: int) -> float:
        """Calculate health based on ant population size."""
        optimal_range = (20, 60)  # Optimal ant population range
        
        if ant_count == 0:
            return 0.0
        elif ant_count < optimal_range[0]:
            return ant_count / optimal_range[0]
        elif ant_count <= optimal_range[1]:
            return 1.0
        else:
            # Overpopulation penalty
            excess = ant_count - optimal_range[1]
            penalty = min(0.5, excess / optimal_range[1])
            return 1.0 - penalty
    
    def _calculate_food_health(self, plant_count: int, fungus_count: int) -> float:
        """Calculate health based on food availability."""
        total_food_sources = plant_count + fungus_count
        optimal_food = 30  # Optimal total food sources
        
        if total_food_sources == 0:
            return 0.0
        elif total_food_sources < optimal_food:
            return total_food_sources / optimal_food
        else:
            return 1.0
    
    def _calculate_predator_balance(self, ant_count: int, predator_count: int) -> float:
        """Calculate health based on predator-prey balance."""
        if ant_count == 0:
            return 1.0 if predator_count == 0 else 0.0
        
        target_ratio = self.config.predator_balance.target_ant_predator_ratio
        if predator_count == 0:
            return 0.8  # Slightly suboptimal but not critical
        
        current_ratio = ant_count / predator_count
        ratio_difference = abs(current_ratio - target_ratio) / target_ratio
        
        return max(0.0, 1.0 - ratio_difference)
    
    def _calculate_parasite_impact(self, ant_count: int, parasite_count: int) -> float:
        """Calculate health impact of parasites."""
        if ant_count == 0:
            return 0.0
        
        if parasite_count == 0:
            return 1.0
        
        parasite_pressure = parasite_count / ant_count
        
        # Parasites become problematic when they exceed 20% of ant population
        if parasite_pressure <= 0.2:
            return 1.0 - (parasite_pressure * 0.5)  # Mild impact
        else:
            return max(0.0, 1.0 - parasite_pressure)
    
    def _calculate_diversity_health(self, ant_count: int, plant_count: int, 
                                   fungus_count: int, parasite_count: int, 
                                   predator_count: int) -> float:
        """Calculate ecosystem diversity health."""
        # Count how many types of entities are present
        types_present = sum([
            ant_count > 0,
            plant_count > 0,
            fungus_count > 0,
            parasite_count > 0,
            predator_count > 0
        ])
        
        # Ideal ecosystem has ants, plants, fungi, and at least one threat
        if types_present >= 4:
            return 1.0
        elif types_present >= 3:
            return 0.8
        elif types_present >= 2:
            return 0.5
        else:
            return 0.0
            
    def record_state(self, environment) -> None:
        """Record current ecosystem state for trend analysis.
        
        Args:
            environment: Current environment state
        """
        health_metrics = self.analyze_ecosystem_health(environment)
        self.balance_history.append(health_metrics) 