"""Enhanced Streamlit app with interactive dashboard for the leafcutter colony simulation."""

import streamlit as st
import sys
import os
from pathlib import Path
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import time

# Add src to path so we can import our modules
current_dir = Path(__file__).parent
src_dir = current_dir.parent / "src"
sys.path.insert(0, str(src_dir))

from src.config import SimulationConfig
from src.simulation import Simulation
from src.balance import EcosystemBalance
from src.visualization import (
    InteractiveGridVisualizer, 
    create_interactive_population_chart,
    create_ecosystem_health_gauge,
    create_spatial_analysis_heatmap
)


def initialize_session_state():
    """Initialize Streamlit session state variables."""
    defaults = {
        'simulation': None,
        'is_running': False,
        'current_step': 0,
        'config': None,
        'balance_analyzer': None,
        'visualizer': None,
        'auto_run': False,
        'show_advanced': False
    }
    
    for key, default_value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = default_value


def create_modern_sidebar():
    """Create a modern, organized sidebar with configuration options."""
    with st.sidebar:
        st.markdown("# 🐜 Simulation Control Center")
        st.markdown("---")
        
        # Quick presets
        st.markdown("### 🎯 Quick Start Presets")
        preset_col1, preset_col2 = st.columns(2)
        
        # Initialize preset values
        if 'preset_values' not in st.session_state:
            st.session_state.preset_values = {}
        
        with preset_col1:
            if st.button("🏞️ Balanced", use_container_width=True):
                st.session_state.preset_values = {
                    'grid_size': 20,
                    'simulation_steps': 150,
                    'initial_ants': 25,
                    'initial_plants': 40,
                    'initial_fungi': 8,
                    'initial_parasites': 3,
                    'initial_predators': 2,
                    'animation_speed': 0.3
                }
                st.rerun()
                
        with preset_col2:
            if st.button("⚡ Dynamic", use_container_width=True):
                st.session_state.preset_values = {
                    'grid_size': 30,
                    'simulation_steps': 200,
                    'initial_ants': 50,
                    'initial_plants': 60,
                    'initial_fungi': 15,
                    'initial_parasites': 8,
                    'initial_predators': 6,
                    'animation_speed': 0.15
                }
                st.rerun()
        
        st.markdown("---")
        
        # Basic Settings (with preset values if available)
        st.markdown("### ⚙️ Basic Settings")
        grid_size = st.slider("🗺️ Grid Size", 10, 50, 
                             st.session_state.preset_values.get('grid_size', 25), 
                             help="Size of the simulation world")
        simulation_steps = st.slider("🔄 Max Steps", 50, 500, 
                                   st.session_state.preset_values.get('simulation_steps', 150), 
                                   help="Maximum simulation steps")
        animation_speed = st.slider("⏱️ Speed (seconds)", 0.01, 2.0, 
                                  st.session_state.preset_values.get('animation_speed', 0.3), 
                                  help="Delay between animation frames")
        
        # Population Settings (with preset values if available)
        st.markdown("### 👥 Initial Populations")
        pop_col1, pop_col2 = st.columns(2)
        
        with pop_col1:
            initial_ants = st.number_input("🐜 Ants", 5, 100, 
                                         st.session_state.preset_values.get('initial_ants', 35), step=5)
            initial_plants = st.number_input("🌿 Plants", 10, 150, 
                                           st.session_state.preset_values.get('initial_plants', 50), step=5)
            initial_fungi = st.number_input("🍄 Fungi", 0, 50, 
                                          st.session_state.preset_values.get('initial_fungi', 12), step=2)
        
        with pop_col2:
            initial_parasites = st.number_input("🦠 Parasites", 0, 20, 
                                              st.session_state.preset_values.get('initial_parasites', 6), step=1)
            initial_predators = st.number_input("🐍 Predators", 0, 15, 
                                              st.session_state.preset_values.get('initial_predators', 4), step=1)
        
        # Advanced Settings Toggle
        st.markdown("---")
        show_advanced = st.checkbox("🔬 Advanced Parameters", value=st.session_state.show_advanced)
        st.session_state.show_advanced = show_advanced
        
        # Always provide default advanced configuration
        advanced_config = {
            'plant_regeneration': {
                'interval': 5,
                'probability': 0.35,
                'max_plants': 70
            },
            'reproduction': {
                'food_threshold': 18,
                'larvae_period': 10,
                'larvae_per_cycle': 2
            },
            'climate': {
                'cycle_length': 30,
                'rain_duration': 12,
                'dry_duration': 18,
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
            }
        }
        
        # Override with user values if advanced mode is enabled
        if show_advanced:
            with st.expander("🌱 Ecosystem Dynamics", expanded=True):
                col1, col2 = st.columns(2)
                with col1:
                    regen_interval = st.slider("Plant Regen Interval", 3, 15, 5)
                    regen_probability = st.slider("Regen Probability", 0.1, 0.8, 0.35)
                with col2:
                    max_plants = st.slider("Max Plants", 30, 200, 70)
                    food_threshold = st.slider("Reproduction Threshold", 5, 30, 18)
            
            with st.expander("🌦️ Climate System", expanded=True):
                col1, col2 = st.columns(2)
                with col1:
                    cycle_length = st.slider("Climate Cycle", 15, 50, 30)
                    rain_duration = st.slider("Rain Duration", 5, 20, 12)
                with col2:
                    dry_duration = st.slider("Dry Duration", 5, 25, 18)
            
            # Update advanced config with user values
            advanced_config = {
                'plant_regeneration': {
                    'interval': regen_interval,
                    'probability': regen_probability,
                    'max_plants': max_plants
                },
                'reproduction': {
                    'food_threshold': food_threshold,
                    'larvae_period': 10,
                    'larvae_per_cycle': 2
                },
                'climate': {
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
                }
            }
        
        # Create configuration - always include all required fields
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
                **advanced_config,
                predator_balance={
                    'target_ant_predator_ratio': 12.0,
                    'spawn_adjustment_rate': 0.1,
                    'base_spawn_chance': 0.05
                },
                parasite_dynamics={
                    'spread_chance': 0.06,
                    'infection_radius': 1
                }
            )
            return config
        except Exception as e:
            st.error(f"Configuration error: {e}")
            return SimulationConfig.get_default()


def create_control_panel():
    """Create a modern control panel with action buttons."""
    st.markdown("### 🎮 Simulation Controls")
    
    col1, col2, col3, col4, col5 = st.columns([1, 1, 1, 1, 1])
    
    with col1:
        init_button = st.button("🎯 Initialize", use_container_width=True, type="primary")
    
    with col2:
        run_button = st.button("▶️ Run Full", use_container_width=True, 
                              disabled=not st.session_state.simulation)
    
    with col3:
        step_button = st.button("⏭️ Step Once", use_container_width=True,
                               disabled=not st.session_state.simulation)
    
    with col4:
        reset_button = st.button("🔄 Reset", use_container_width=True,
                                disabled=not st.session_state.simulation)
    
    with col5:
        auto_toggle = st.checkbox("🔁 Auto-run", value=st.session_state.auto_run)
        st.session_state.auto_run = auto_toggle
    
    return init_button, run_button, step_button, reset_button


def display_live_metrics_dashboard(simulation: Simulation):
    """Display a comprehensive live metrics dashboard."""
    status = simulation.get_status()
    
    # Top metrics row
    st.markdown("### 📊 Live Ecosystem Metrics")
    metric_cols = st.columns(6)
    
    metrics_data = [
        ("Step", f"{status['step']}/{status['max_steps']}", "🔄"),
        ("Ants", status['entity_counts']['ants'], "🐜"),
        ("Plants", status['entity_counts']['plants'], "🌿"),
        ("Fungi", status['entity_counts']['fungi'], "🍄"),
        ("Parasites", status['entity_counts']['parasites'], "🦠"),
        ("Predators", status['entity_counts']['predators'], "🐍")
    ]
    
    for i, (label, value, icon) in enumerate(metrics_data):
        with metric_cols[i]:
            st.metric(f"{icon} {label}", value)
    
    # Progress and status row
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        progress = status['progress_percent'] / 100.0
        st.progress(progress, text=f"Progress: {status['progress_percent']:.1f}%")
    
    with col2:
        climate_emoji = "🌧️" if status['climate'] == 'rain' else "☀️"
        st.metric(f"{climate_emoji} Climate", status['climate'].title())
    
    with col3:
        risk_colors = {
            'Low': '🟢', 'Medium': '🟡', 'High': '🟠', 
            'Critical': '🔴', 'Extinct': '⚫'
        }
        risk_emoji = risk_colors.get(status['extinction_risk'], '🔵')
        st.metric(f"{risk_emoji} Risk", status['extinction_risk'])


def create_main_dashboard():
    """Create the main dashboard layout with improved organization."""
    # Header with status
    st.markdown("# 🌿 Leafcutter Colony Ecosystem Simulation")
    st.markdown("**Interactive ecological simulation with advanced dynamics and real-time analytics**")
    
    if st.session_state.simulation:
        # Live metrics in a clean header
        display_live_metrics_dashboard(st.session_state.simulation)
        
        st.markdown("---")
        
        # Main content - organized in a clean grid layout
        # Row 1: Main simulation grid (centered) + Controls
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col1:
            st.markdown("### 🗝️ Entity Guide")
            if st.session_state.visualizer:
                legend_fig = st.session_state.visualizer.create_entity_legend()
                st.plotly_chart(legend_fig, use_container_width=True, key="legend", config={'displayModeBar': False})
        
        with col2:
            st.markdown("### 🗺️ Interactive Ecosystem Map")
            # Ensure stable centering with container
            grid_container = st.container()
            with grid_container:
                if st.session_state.visualizer:
                    try:
                        grid_fig = st.session_state.visualizer.create_interactive_grid(
                            st.session_state.simulation.environment
                        )
                        # Fixed positioning to prevent flickering
                        st.plotly_chart(
                            grid_fig, 
                            use_container_width=False, 
                            key="main_grid",
                            config={
                                'displayModeBar': False, 
                                'staticPlot': False,
                                'responsive': False  # Prevent responsive resizing
                            }
                        )
                    except Exception as e:
                        st.error(f"Visualization error: {e}")
                        st.text("Fallback text display:")
                        st.text(st.session_state.simulation.environment.render_grid())
        
        with col3:
            st.markdown("### 🌿 Health Monitor")
            if st.session_state.balance_analyzer:
                health_fig = create_ecosystem_health_gauge(
                    st.session_state.balance_analyzer, 
                    st.session_state.simulation
                )
                st.plotly_chart(health_fig, use_container_width=True, key="health", config={'displayModeBar': False})
        
        # Row 2: Ecosystem Analysis (if available)
        if st.session_state.balance_analyzer:
            st.markdown("---")
            st.markdown("### 📊 Ecosystem Analysis")
            
            analysis_col1, analysis_col2, analysis_col3 = st.columns(3)
            
            with analysis_col1:
                st.markdown("#### 🔍 Health Components")
                health_scores = st.session_state.balance_analyzer.analyze_ecosystem_health(st.session_state.simulation.environment)
                
                # Create a clean health component display
                for component, score in health_scores.items():
                    if component != 'overall':
                        # Use colored metrics instead of markdown
                        if score > 0.7:
                            st.success(f"**{component.title()}**: {score:.2f}")
                        elif score > 0.4:
                            st.warning(f"**{component.title()}**: {score:.2f}")
                        else:
                            st.error(f"**{component.title()}**: {score:.2f}")
            
            with analysis_col2:
                st.markdown("#### 🎯 Current Status")
                sustainability_score, assessment = st.session_state.balance_analyzer.calculate_sustainability_score(st.session_state.simulation.environment)
                
                # Status metrics
                status = st.session_state.simulation.get_status()
                st.metric("🏆 Overall Health", f"{health_scores['overall']:.2f}")
                st.metric("📈 Sustainability", f"{sustainability_score:.2f}")
                st.metric("⚠️ Risk Level", status['extinction_risk'])
            
            with analysis_col3:
                st.markdown("#### 🌍 Environment")
                status = st.session_state.simulation.get_status()
                
                # Environment metrics
                st.metric("🌦️ Climate", status['climate'].title())
                st.metric("🍄 Food Stock", f"{status['total_food']:.1f}")
                st.metric("🔄 Progress", f"{status['progress_percent']:.1f}%")
    
    else:
        # Welcome screen - much cleaner layout
        st.markdown("---")
        
        # Centered welcome message
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col2:
            st.markdown("### 🚀 Welcome to the Advanced Ecosystem Simulation!")
            
            # Feature highlights in organized cards
            st.markdown("""
            <div style="background-color: #f8f9fa; padding: 2rem; border-radius: 10px; border-left: 5px solid #3498db;">
            <h4>🎯 Key Features:</h4>
            <ul>
                <li><strong>🖱️ Interactive Grid</strong> - Hover over entities for detailed information</li>
                <li><strong>📊 Real-time Analytics</strong> - Live ecosystem health monitoring</li>
                <li><strong>🌦️ Dynamic Climate</strong> - Weather affects plant growth and predator behavior</li>
                <li><strong>⚖️ Adaptive Balance</strong> - Smart ecosystem management prevents extinctions</li>
                <li><strong>📈 Advanced Visualizations</strong> - Professional charts and interactive plots</li>
            </ul>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("")
            
            st.markdown("""
            <div style="background-color: #e8f5e8; padding: 2rem; border-radius: 10px; border-left: 5px solid #27ae60;">
            <h4>🎮 Getting Started:</h4>
            <ol>
                <li><strong>Configure</strong> parameters in the sidebar (try the presets!)</li>
                <li><strong>Initialize</strong> the simulation ecosystem</li>
                <li><strong>Run</strong> full simulation or step through manually</li>
                <li><strong>Explore</strong> different views and analytics</li>
                <li><strong>Export</strong> data for further analysis</li>
            </ol>
            </div>
            """, unsafe_allow_html=True)
            
            # Call to action
            st.markdown("")
            st.info("👈 **Configure your simulation parameters in the sidebar and click 'Initialize' to begin!**", icon="🎯")


def create_analytics_dashboard():
    """Create advanced analytics dashboard."""
    st.markdown("# 📈 Advanced Analytics Dashboard")
    
    if not st.session_state.simulation:
        st.warning("Initialize and run a simulation to view analytics!")
        return
    
    # Population trends
    st.markdown("### 📊 Population Dynamics")
    pop_fig = create_interactive_population_chart(st.session_state.simulation)
    st.plotly_chart(pop_fig, use_container_width=True, key="population_trends")
    
    # Spatial analysis
    if st.button("🗺️ Generate Spatial Analysis", use_container_width=True):
        st.markdown("### 🗺️ Spatial Distribution Analysis")
        spatial_fig = create_spatial_analysis_heatmap(
            st.session_state.simulation.environment,
            st.session_state.config.grid_size
        )
        st.plotly_chart(spatial_fig, use_container_width=True, key="spatial_analysis")
    
    # Export section
    st.markdown("---")
    st.markdown("### 📥 Data Export")
    
    export_col1, export_col2 = st.columns(2)
    
    with export_col1:
        if st.button("📋 Export Summary JSON", use_container_width=True):
            summary = st.session_state.simulation.export_metrics_summary()
            st.json(summary)
    
    with export_col2:
        metrics = st.session_state.simulation.get_metrics()
        if metrics['step']:
            df = pd.DataFrame(metrics)
            csv = df.to_csv(index=False)
            st.download_button(
                label="📊 Download Metrics CSV",
                data=csv,
                file_name=f"simulation_metrics_{int(time.time())}.csv",
                mime="text/csv",
                use_container_width=True
            )


def handle_simulation_controls(config, init_button, run_button, step_button, reset_button):
    """Handle all simulation control logic."""
    # Initialize simulation
    if init_button:
        st.session_state.simulation = Simulation(config)
        st.session_state.balance_analyzer = EcosystemBalance(config)
        st.session_state.visualizer = InteractiveGridVisualizer(config.grid_size)
        st.session_state.is_running = False
        st.session_state.current_step = 0
        st.success("🎯 Simulation initialized successfully!")
        st.rerun()
    
    # Run full simulation
    if run_button and st.session_state.simulation:
        st.session_state.is_running = True
        
        # Create container for live updates
        with st.container():
            status_placeholder = st.empty()
            grid_placeholder = st.empty()
            
            # Run simulation with live updates
            for step, grid_state in enumerate(st.session_state.simulation.run_with_delay()):
                with status_placeholder.container():
                    display_live_metrics_dashboard(st.session_state.simulation)
                
                with grid_placeholder.container():
                    if st.session_state.visualizer:
                        grid_fig = st.session_state.visualizer.create_interactive_grid(
                            st.session_state.simulation.environment
                        )
                        st.plotly_chart(grid_fig, use_container_width=True, key=f"live_grid_{step}")
                
                # Update balance analyzer
                if st.session_state.balance_analyzer:
                    st.session_state.balance_analyzer.record_state(
                        st.session_state.simulation.environment
                    )
        
        st.session_state.is_running = False
        st.success("✅ Simulation completed!")
    
    # Step once
    if step_button and st.session_state.simulation:
        st.session_state.simulation.step_once()
        st.session_state.current_step = st.session_state.simulation.current_step
        
        if st.session_state.balance_analyzer:
            st.session_state.balance_analyzer.record_state(
                st.session_state.simulation.environment
            )
        st.rerun()
    
    # Reset simulation
    if reset_button and st.session_state.simulation:
        st.session_state.simulation.reset()
        st.session_state.balance_analyzer = EcosystemBalance(config)
        st.session_state.is_running = False
        st.session_state.current_step = 0
        st.success("🔄 Simulation reset!")
        st.rerun()


def main():
    """Main application with enhanced UI/UX."""
    st.set_page_config(
        page_title="🌿 Leafcutter Colony Simulation",
        page_icon="🐜",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Custom CSS for clean, minimal styling with pleasant UX touches
    st.markdown("""
    <style>
    /* Main layout */
    .main > div {
        padding-top: 1rem;
    }
    
    /* Clean metrics styling with subtle hover effect */
    .stMetric {
        background-color: #f8f9fa;
        border: 1px solid #e9ecef;
        padding: 0.75rem;
        border-radius: 6px;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        transition: box-shadow 0.2s ease;
    }
    
    .stMetric:hover {
        box-shadow: 0 2px 6px rgba(0,0,0,0.15);
    }
    
    /* Enhanced button styling with pleasant effects */
    .stButton > button {
        border-radius: 6px;
        border: 1px solid #ddd;
        padding: 0.5rem 1rem;
        font-weight: 500;
        transition: all 0.2s ease;
        background: linear-gradient(145deg, #ffffff, #f5f5f5);
    }
    
    .stButton > button:hover {
        box-shadow: 0 3px 8px rgba(0,0,0,0.12);
        border-color: #3498db;
        transform: translateY(-1px);
    }
    
    .stButton > button[kind="primary"] {
        background: linear-gradient(145deg, #3498db, #2980b9);
        color: white;
        border-color: #3498db;
    }
    
    .stButton > button[kind="primary"]:hover {
        background: linear-gradient(145deg, #2980b9, #1f5582);
        transform: translateY(-1px);
    }
    
    /* Ensure stable grid positioning */
    .plotly-graph-div {
        margin: 0 auto !important;
        display: block !important;
        position: relative !important;
    }
    
    /* Clean header styling */
    h1 {
        color: #2c3e50;
        text-align: center;
        margin-bottom: 0.5rem;
    }
    
    h3 {
        color: #34495e;
        margin-bottom: 1rem;
        font-weight: 600;
    }
    
    /* Minimal separator styling */
    hr {
        margin: 1rem 0;
        border: none;
        border-top: 1px solid #e9ecef;
    }
    
    /* Clean message styling */
    .stSuccess, .stWarning, .stError {
        border-radius: 6px;
        padding: 0.75rem;
        margin: 0.5rem 0;
        border-left: 4px solid;
    }
    
    .stSuccess {
        border-left-color: #27ae60;
        background-color: #d4edda;
    }
    
    .stWarning {
        border-left-color: #f39c12;
        background-color: #fff3cd;
    }
    
    .stError {
        border-left-color: #e74c3c;
        background-color: #f8d7da;
    }
    
    /* Pleasant info box */
    .stInfo {
        border-radius: 6px;
        padding: 1rem;
        border-left: 4px solid #3498db;
        background-color: #e3f2fd;
    }
    
    /* Subtle container improvements */
    .element-container {
        margin-bottom: 0.5rem;
    }
    
    /* Smooth progress bar */
    .stProgress > div > div > div > div {
        border-radius: 4px;
        transition: width 0.3s ease;
    }
    
    /* Pleasant sidebar styling */
    .sidebar .sidebar-content {
        background: linear-gradient(180deg, #fafafa 0%, #f0f0f0 100%);
    }
    
    /* Subtle chart container enhancement */
    .js-plotly-plot {
        border-radius: 8px;
        transition: all 0.2s ease;
    }
    
    .js-plotly-plot:hover {
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    }
    </style>
    """, unsafe_allow_html=True)
    
    initialize_session_state()
    
    # Sidebar configuration
    config = create_modern_sidebar()
    st.session_state.config = config
    
    # Navigation
    tab1, tab2 = st.tabs(["🎮 Main Dashboard", "📈 Analytics"])
    
    with tab1:
        # Control panel
        init_button, run_button, step_button, reset_button = create_control_panel()
        
        # Handle controls
        handle_simulation_controls(config, init_button, run_button, step_button, reset_button)
        
        # Main dashboard
        create_main_dashboard()
        
        # Auto-run functionality
        if st.session_state.auto_run and st.session_state.simulation and not st.session_state.is_running:
            time.sleep(config.animation_speed)
            if st.session_state.simulation.current_step < config.simulation_steps:
                st.session_state.simulation.step_once()
                if st.session_state.balance_analyzer:
                    st.session_state.balance_analyzer.record_state(
                        st.session_state.simulation.environment
                    )
                st.rerun()
    
    with tab2:
        create_analytics_dashboard()
    
    # Footer
    st.markdown("---")
    st.markdown(
        "**🐜 Enhanced Leafcutter Colony Simulation** • "
        "Built with Streamlit & Plotly • "
        "Interactive ecosystem modeling for research and education"
    )


if __name__ == "__main__":
    main() 