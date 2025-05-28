"""Tests for the Simulation class."""

import pytest
import sys
from pathlib import Path

# Add src to path
src_dir = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_dir))

from config import SimulationConfig
from simulation import Simulation


class TestSimulation:
    """Test cases for Simulation class."""
    
    def test_simulation_initialization(self):
        """Test simulation initializes correctly."""
        config = SimulationConfig.get_default()
        sim = Simulation(config)
        
        assert sim.config == config
        assert sim.environment is not None
        assert sim.is_running is False
        assert sim.current_step == 0
    
    def test_simulation_step_once(self):
        """Test single step functionality."""
        config = SimulationConfig.get_default()
        sim = Simulation(config)
        
        initial_step = sim.current_step
        grid_state = sim.step_once()
        
        assert sim.current_step == initial_step + 1
        assert isinstance(grid_state, str)
    
    def test_simulation_reset(self):
        """Test simulation reset functionality."""
        config = SimulationConfig.get_default()
        sim = Simulation(config)
        
        # Run a few steps
        sim.step_once()
        sim.step_once()
        
        assert sim.current_step > 0
        
        # Reset
        sim.reset()
        
        assert sim.current_step == 0
        assert sim.is_running is False
    
    def test_simulation_run_generator(self):
        """Test simulation run generator."""
        config = SimulationConfig.get_default()
        config.simulation_steps = 5  # Short simulation for testing
        sim = Simulation(config)
        
        states = list(sim.run())
        
        # Should have initial state + 5 steps = 6 total states
        assert len(states) >= 5
        assert all(isinstance(state, str) for state in states)
    
    def test_get_status(self):
        """Test status reporting."""
        config = SimulationConfig.get_default()
        sim = Simulation(config)
        
        status = sim.get_status()
        
        assert 'step' in status
        assert 'max_steps' in status
        assert 'is_running' in status
        assert 'entity_counts' in status
        assert 'extinction_risk' in status
    
    def test_get_metrics(self):
        """Test metrics retrieval."""
        config = SimulationConfig.get_default()
        sim = Simulation(config)
        
        # Run a few steps to generate metrics
        sim.step_once()
        sim.step_once()
        
        metrics = sim.get_metrics()
        
        assert 'step' in metrics
        assert 'ant_count' in metrics
        assert 'plant_count' in metrics
        assert len(metrics['step']) > 0
    
    def test_export_metrics_summary(self):
        """Test metrics summary export."""
        config = SimulationConfig.get_default()
        sim = Simulation(config)
        
        # Run a few steps
        sim.step_once()
        sim.step_once()
        
        summary = sim.export_metrics_summary()
        
        assert 'total_steps' in summary
        assert 'final_counts' in summary
        assert 'peak_counts' in summary
        assert 'average_counts' in summary
        assert 'colony_survived' in summary 