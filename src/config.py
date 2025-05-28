"""Configuration management for the leafcutter colony simulation."""

from typing import Dict, Any
import yaml
from pathlib import Path
from pydantic import BaseModel, Field, validator


class PlantRegenerationConfig(BaseModel):
    """Configuration for plant regeneration mechanics."""
    interval: int = Field(gt=0, description="Steps between regeneration attempts")
    probability: float = Field(ge=0, le=1, description="Chance of new plant per attempt")
    max_plants: int = Field(gt=0, description="Maximum plants on grid")


class ReproductionConfig(BaseModel):
    """Configuration for ant reproduction mechanics."""
    food_threshold: int = Field(gt=0, description="Fungi needed for reproduction")
    larvae_period: int = Field(gt=0, description="Steps between reproduction attempts")
    larvae_per_cycle: int = Field(gt=0, description="New ants per successful reproduction")


class ClimateEffects(BaseModel):
    """Climate effect multipliers."""
    plant_regen_multiplier: float = Field(gt=0, description="Plant regeneration rate modifier")
    predator_spawn_reduction: float = Field(ge=0, description="Predator spawn rate modifier")
    predator_spawn_increase: float = Field(ge=0, description="Predator spawn rate modifier")


class ClimateConfig(BaseModel):
    """Configuration for climate cycles."""
    cycle_length: int = Field(gt=0, description="Steps between climate changes")
    rain_duration: int = Field(gt=0, description="Steps of rainy weather")
    dry_duration: int = Field(gt=0, description="Steps of dry weather")
    rain_effects: ClimateEffects
    dry_effects: ClimateEffects
    
    @validator('rain_duration', 'dry_duration')
    def validate_duration(cls, v, values):
        """Ensure durations don't exceed cycle length."""
        if 'cycle_length' in values and v > values['cycle_length']:
            raise ValueError("Duration cannot exceed cycle length")
        return v


class PredatorBalanceConfig(BaseModel):
    """Configuration for predator-prey balance."""
    target_ant_predator_ratio: float = Field(gt=0, description="Optimal ants per predator")
    spawn_adjustment_rate: float = Field(ge=0, le=1, description="Rate of spawn adjustment")
    base_spawn_chance: float = Field(ge=0, le=1, description="Baseline predator spawn probability")


class ParasiteDynamicsConfig(BaseModel):
    """Configuration for parasite behavior."""
    spread_chance: float = Field(ge=0, le=1, description="Probability of new parasite per step")
    infection_radius: int = Field(ge=0, description="Distance for parasite effects")


class SimulationConfig(BaseModel):
    """Complete simulation configuration."""
    
    # Grid Configuration
    grid_size: int = Field(ge=5, le=100, description="Grid dimensions (NxN)")
    simulation_steps: int = Field(gt=0, description="Total simulation steps")
    animation_speed: float = Field(gt=0, description="Delay between frames in seconds")
    
    # Initial Populations
    initial_ants: int = Field(ge=1, description="Starting number of ants")
    initial_plants: int = Field(ge=0, description="Starting number of plants")
    initial_fungi: int = Field(ge=0, description="Starting number of fungi")
    initial_parasites: int = Field(ge=0, description="Starting number of parasites")
    initial_predators: int = Field(ge=0, description="Starting number of predators")
    
    # Subsystem Configurations
    plant_regeneration: PlantRegenerationConfig
    reproduction: ReproductionConfig
    climate: ClimateConfig
    predator_balance: PredatorBalanceConfig
    parasite_dynamics: ParasiteDynamicsConfig
    
    @validator('initial_plants')
    def validate_initial_plants(cls, v, values):
        """Ensure initial plants don't exceed regeneration maximum."""
        if 'plant_regeneration' in values and v > values['plant_regeneration'].max_plants:
            raise ValueError("Initial plants cannot exceed maximum plants")
        return v
    
    @classmethod
    def from_yaml(cls, yaml_path: str) -> "SimulationConfig":
        """Load configuration from YAML file."""
        path = Path(yaml_path)
        if not path.exists():
            raise FileNotFoundError(f"Configuration file not found: {yaml_path}")
        
        with open(path, 'r') as f:
            data = yaml.safe_load(f)
        
        return cls(**data)
    
    @classmethod
    def get_default(cls) -> "SimulationConfig":
        """Get default configuration."""
        try:
            return cls.from_yaml("data/default_params.yaml")
        except FileNotFoundError:
            # Fallback to hardcoded defaults if file not found
            return cls(
                grid_size=20,
                simulation_steps=100,
                animation_speed=0.2,
                initial_ants=30,
                initial_plants=40,
                initial_fungi=10,
                initial_parasites=5,
                initial_predators=3,
                plant_regeneration=PlantRegenerationConfig(
                    interval=5, probability=0.3, max_plants=60
                ),
                reproduction=ReproductionConfig(
                    food_threshold=15, larvae_period=10, larvae_per_cycle=1
                ),
                climate=ClimateConfig(
                    cycle_length=25,
                    rain_duration=10,
                    dry_duration=15,
                    rain_effects=ClimateEffects(
                        plant_regen_multiplier=2.0,
                        predator_spawn_reduction=0.5,
                        predator_spawn_increase=1.0
                    ),
                    dry_effects=ClimateEffects(
                        plant_regen_multiplier=0.3,
                        predator_spawn_reduction=1.0,
                        predator_spawn_increase=1.5
                    )
                ),
                predator_balance=PredatorBalanceConfig(
                    target_ant_predator_ratio=10.0,
                    spawn_adjustment_rate=0.1,
                    base_spawn_chance=0.05
                ),
                parasite_dynamics=ParasiteDynamicsConfig(
                    spread_chance=0.05, infection_radius=1
                )
            ) 