"""Tests for the Environment class."""

import pytest
import sys
from pathlib import Path

# Add src to path
src_dir = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_dir))

from config import SimulationConfig
from environment import Environment
from models import Ant, Plant, Fungus, Parasite, Predator


class TestEnvironment:
    """Test cases for Environment class."""
    
    def test_environment_initialization(self):
        """Test environment initializes correctly."""
        config = SimulationConfig.get_default()
        env = Environment(config)
        
        assert env.grid_size == config.grid_size
        assert len(env.ants) == config.initial_ants
        assert len(env.plants) == config.initial_plants
        assert len(env.fungi) == config.initial_fungi
        assert len(env.parasites) == config.initial_parasites
        assert len(env.predators) == config.initial_predators
    
    def test_environment_step(self):
        """Test environment step functionality."""
        config = SimulationConfig.get_default()
        env = Environment(config)
        
        initial_step = env.step_count
        env.step()
        
        assert env.step_count == initial_step + 1
    
    def test_add_entities(self):
        """Test adding entities to environment."""
        config = SimulationConfig.get_default()
        env = Environment(config)
        
        initial_ant_count = len(env.ants)
        env.add_ant((5, 5))
        assert len(env.ants) == initial_ant_count + 1
        
        initial_plant_count = len(env.plants)
        env.add_plant((6, 6))
        assert len(env.plants) == initial_plant_count + 1
    
    def test_render_grid(self):
        """Test grid rendering functionality."""
        config = SimulationConfig.get_default()
        config.grid_size = 5  # Small grid for testing
        env = Environment(config)
        
        grid_string = env.render_grid()
        
        # Check that grid is correct size
        lines = grid_string.split('\n')
        assert len(lines) == 5
        assert all(len(line) == 5 for line in lines)
    
    def test_entity_cleanup(self):
        """Test that inactive entities are removed."""
        config = SimulationConfig.get_default()
        env = Environment(config)
        
        # Deactivate an ant
        if env.ants:
            env.ants[0].deactivate()
            initial_count = len(env.ants)
            
            env._cleanup_entities()
            
            assert len(env.ants) == initial_count - 1
    
    def test_get_entity_counts(self):
        """Test entity count reporting."""
        config = SimulationConfig.get_default()
        env = Environment(config)
        
        counts = env.get_entity_counts()
        
        assert 'ants' in counts
        assert 'plants' in counts
        assert 'fungi' in counts
        assert 'parasites' in counts
        assert 'predators' in counts
        
        assert counts['ants'] == len(env.ants)
        assert counts['plants'] == len(env.plants) 