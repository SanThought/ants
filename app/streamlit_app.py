"""Streamlit app for the leafcutter colony simulation."""

import streamlit as st
import sys
import os
from pathlib import Path
import pandas as pd
import numpy as np

# Add src to path so we can import our modules
current_dir = Path(__file__).parent
src_dir = current_dir.parent / "src"
sys.path.insert(0, str(src_dir))

from src.config import SimulationConfig
from src.simulation import Simulation
from src.balance import EcosystemBalance


def initialize_session_state():
    """Initialize Streamlit session state variables."""
    if 'simulation' not in st.session_state:
        st.session_state.simulation = None
    if 'is_running' not in st.session_state:
        st.session_state.is_running = False
    if 'current_step' not in st.session_state:
        st.session_state.current_step = 0
    if 'config' not in st.session_state:
        st.session_state.config = None
    if 'balance_analyzer' not in st.session_state:
        st.session_state.balance_analyzer = None


def create_config_from_ui() -> SimulationConfig:
    """Create simulation configuration from UI inputs."""
    st.sidebar.header("🔧 Simulation Parameters")
    
    # Basic parameters
    st.sidebar.subheader("Basic Settings")
    grid_size = st.sidebar.slider("Grid Size (NxN)", 10, 50, 20)
    simulation_steps = st.sidebar.slider("Simulation Steps", 50, 500, 100)
    animation_speed = st.sidebar.slider("Animation Speed (s)", 0.01, 2.0, 0.2)
    
    # Initial populations
    st.sidebar.subheader("Initial Populations")
    initial_ants = st.sidebar.slider("Ants", 5, 100, 30)
    initial_plants = st.sidebar.slider("Plants", 10, 150, 40)
    initial_fungi = st.sidebar.slider("Fungi", 0, 50, 10)
    initial_parasites = st.sidebar.slider("Parasites", 0, 20, 5)
    initial_predators = st.sidebar.slider("Predators", 0, 15, 3)
    
    # Advanced parameters
    with st.sidebar.expander("🌱 Plant Regeneration"):
        regen_interval = st.slider("Regeneration Interval", 3, 15, 5)
        regen_probability = st.slider("Regeneration Probability", 0.1, 0.8, 0.3)
        max_plants = st.slider("Maximum Plants", 30, 200, 60)
    
    with st.sidebar.expander("🐜 Reproduction"):
        food_threshold = st.slider("Food Threshold", 5, 30, 15)
        larvae_period = st.slider("Reproduction Period", 5, 20, 10)
        larvae_per_cycle = st.slider("New Ants per Cycle", 1, 5, 1)
    
    with st.sidebar.expander("🌦️ Climate"):
        cycle_length = st.slider("Climate Cycle Length", 15, 50, 25)
        rain_duration = st.slider("Rain Duration", 5, 20, 10)
        dry_duration = st.slider("Dry Duration", 5, 25, 15)
    
    # Create configuration
    try:
        config = SimulationConfig(
            grid_size=grid_size,
            simulation_steps=simulation_steps,
            animation_speed=animation_speed,
            initial_ants=initial_ants,
            initial_plants=initial_plants,
            initial_fungi=initial_fungi,
            initial_parasites=initial_parasites,
            initial_predators=initial_predators,
            plant_regeneration={
                'interval': regen_interval,
                'probability': regen_probability,
                'max_plants': max_plants
            },
            reproduction={
                'food_threshold': food_threshold,
                'larvae_period': larvae_period,
                'larvae_per_cycle': larvae_per_cycle
            },
            climate={
                'cycle_length': cycle_length,
                'rain_duration': rain_duration,
                'dry_duration': dry_duration,
                'rain_effects': {
                    'plant_regen_multiplier': 2.0,
                    'predator_spawn_reduction': 0.5,
                    'predator_spawn_increase': 1.0
                },
                'dry_effects': {
                    'plant_regen_multiplier': 0.3,
                    'predator_spawn_reduction': 1.0,
                    'predator_spawn_increase': 1.5
                }
            },
            predator_balance={
                'target_ant_predator_ratio': 10.0,
                'spawn_adjustment_rate': 0.1,
                'base_spawn_chance': 0.05
            },
            parasite_dynamics={
                'spread_chance': 0.05,
                'infection_radius': 1
            }
        )
        return config
    except Exception as e:
        st.error(f"Configuration error: {e}")
        return SimulationConfig.get_default()


def display_simulation_grid(simulation: Simulation):
    """Display the simulation grid in a monospace format."""
    grid_state = simulation.environment.render_grid()
    
    # Use monospace font for proper grid alignment
    st.text(grid_state)


def display_metrics_dashboard(simulation: Simulation):
    """Display real-time metrics and statistics."""
    status = simulation.get_status()
    
    # Main metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Step", f"{status['step']}/{status['max_steps']}")
        st.metric("Ants", status['entity_counts']['ants'])
    
    with col2:
        st.metric("Plants", status['entity_counts']['plants'])
        st.metric("Fungi", status['entity_counts']['fungi'])
    
    with col3:
        st.metric("Parasites", status['entity_counts']['parasites'])
        st.metric("Predators", status['entity_counts']['predators'])
    
    with col4:
        st.metric("Climate", status['climate'].title())
        st.metric("Food Stock", f"{status['total_food']:.1f}")
    
    # Progress bar
    progress = status['progress_percent'] / 100.0
    st.progress(progress)
    
    # Risk assessment
    risk_color = {
        'Low': 'green',
        'Medium': 'orange', 
        'High': 'red',
        'Critical': 'red',
        'Extinct': 'gray'
    }.get(status['extinction_risk'], 'blue')
    
    st.markdown(f"**Extinction Risk:** :{risk_color}[{status['extinction_risk']}]")


def display_ecosystem_analysis(balance_analyzer: EcosystemBalance, simulation: Simulation):
    """Display ecosystem health analysis."""
    st.subheader("🌿 Ecosystem Health Analysis")
    
    health_scores = balance_analyzer.analyze_ecosystem_health(simulation.environment)
    
    # Health metrics
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Health Components:**")
        for component, score in health_scores.items():
            if component != 'overall':
                color = 'green' if score > 0.7 else 'orange' if score > 0.4 else 'red'
                st.markdown(f"- {component.title()}: :{color}[{score:.2f}]")
    
    with col2:
        overall_score = health_scores['overall']
        score_color = 'green' if overall_score > 0.7 else 'orange' if overall_score > 0.4 else 'red'
        st.metric("Overall Health", f"{overall_score:.2f}", delta_color="normal")
        
        # Sustainability assessment
        sustainability_score, assessment = balance_analyzer.calculate_sustainability_score(simulation.environment)
        st.write(f"**Assessment:** {assessment}")


def display_population_charts(simulation: Simulation):
    """Display population trends over time."""
    metrics = simulation.get_metrics()
    
    if not metrics['step']:
        st.info("Run simulation to see population trends")
        return
    
    # Create DataFrame for plotting
    df = pd.DataFrame({
        'Step': metrics['step'],
        'Ants': metrics['ant_count'],
        'Plants': metrics['plant_count'],
        'Fungi': metrics['fungus_count'],
        'Parasites': metrics['parasite_count'],
        'Predators': metrics['predator_count']
    })
    
    # Population trends chart
    st.subheader("📊 Population Trends")
    st.line_chart(df.set_index('Step'))
    
    # Food stock chart
    if metrics['food_stock']:
        food_df = pd.DataFrame({
            'Step': metrics['step'],
            'Food Stock': metrics['food_stock']
        })
        st.subheader("🍄 Food Stock Over Time")
        st.line_chart(food_df.set_index('Step'))


def main():
    """Main Streamlit app."""
    st.set_page_config(
        page_title="🌿 Leafcutter Colony Simulation",
        page_icon="🐜",
        layout="wide"
    )
    
    st.title("🌿 Leafcutter Colony Ecosystem Simulation")
    st.markdown("An interactive simulation of ant colony dynamics with ecological balance")
    
    initialize_session_state()
    
    # Configuration
    config = create_config_from_ui()
    st.session_state.config = config
    
    # Control buttons
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("🎯 Initialize Simulation"):
            st.session_state.simulation = Simulation(config)
            st.session_state.balance_analyzer = EcosystemBalance(config)
            st.session_state.is_running = False
            st.session_state.current_step = 0
            st.success("Simulation initialized!")
    
    with col2:
        if st.button("▶️ Run Full Simulation") and st.session_state.simulation:
            st.session_state.is_running = True
            
            # Run simulation with progress display
            grid_placeholder = st.empty()
            metrics_placeholder = st.empty()
            
            for grid_state in st.session_state.simulation.run_with_delay():
                with grid_placeholder.container():
                    st.text(grid_state)
                
                with metrics_placeholder.container():
                    display_metrics_dashboard(st.session_state.simulation)
                
                # Update balance analyzer
                if st.session_state.balance_analyzer:
                    st.session_state.balance_analyzer.record_state(st.session_state.simulation.environment)
            
            st.session_state.is_running = False
            st.success("Simulation completed!")
    
    with col3:
        if st.button("⏭️ Step Once") and st.session_state.simulation:
            grid_state = st.session_state.simulation.step_once()
            st.session_state.current_step = st.session_state.simulation.current_step
            
            if st.session_state.balance_analyzer:
                st.session_state.balance_analyzer.record_state(st.session_state.simulation.environment)
    
    with col4:
        if st.button("🔄 Reset") and st.session_state.simulation:
            st.session_state.simulation.reset()
            st.session_state.balance_analyzer = EcosystemBalance(config)
            st.session_state.is_running = False
            st.session_state.current_step = 0
            st.success("Simulation reset!")
    
    # Display current state
    if st.session_state.simulation:
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.subheader("🎮 Simulation Grid")
            display_simulation_grid(st.session_state.simulation)
        
        with col2:
            st.subheader("📊 Metrics")
            display_metrics_dashboard(st.session_state.simulation)
        
        # Ecosystem analysis
        if st.session_state.balance_analyzer:
            display_ecosystem_analysis(st.session_state.balance_analyzer, st.session_state.simulation)
        
        # Population charts
        display_population_charts(st.session_state.simulation)
        
        # Export results
        if st.button("📥 Export Results"):
            summary = st.session_state.simulation.export_metrics_summary()
            st.json(summary)
            
            # Convert metrics to CSV
            metrics = st.session_state.simulation.get_metrics()
            if metrics['step']:
                df = pd.DataFrame(metrics)
                csv = df.to_csv(index=False)
                st.download_button(
                    label="Download CSV",
                    data=csv,
                    file_name="simulation_metrics.csv",
                    mime="text/csv"
                )
    
    else:
        st.info("👆 Click 'Initialize Simulation' to begin")
        
        # Display legend
        st.subheader("🗝️ Symbol Legend")
        legend_col1, legend_col2 = st.columns(2)
        
        with legend_col1:
            st.write("- 🟠 Ants")
            st.write("- 🌿 Plants") 
            st.write("- 🍄 Fungi")
        
        with legend_col2:
            st.write("- 🧫 Parasites")
            st.write("- 🐍 Predators")
            st.write("- ⬛ Empty space")
    
    # Footer
    st.markdown("---")
    st.markdown("Built with Streamlit • 🐜 Inspired by leafcutter ant research")


if __name__ == "__main__":
    main() 