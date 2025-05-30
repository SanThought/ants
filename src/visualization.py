"""Enhanced interactive visualization module using Plotly for the leafcutter colony simulation."""

import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Optional
import plotly.colors as pc

# Enhanced color scheme with better visual appeal
ENTITY_COLORS = {
    'empty': '#1a1a1a',      # Dark background
    'ant': '#FF6B35',        # Vibrant orange for ants
    'plant': '#2ECC71',      # Fresh green for plants
    'fungus': '#8E44AD',     # Purple for fungi (more distinct)
    'parasite': '#E74C3C',   # Red for parasites
    'predator': '#F39C12',   # Gold for predators
    'trail': '#FFF3E0'       # Light trail color
}

# Entity symbols and descriptions
ENTITY_INFO = {
    'ant': {'symbol': '🐜', 'name': 'Worker Ant', 'description': 'Foraging and building the colony'},
    'plant': {'symbol': '🌿', 'name': 'Plant', 'description': 'Food source for harvesting'},
    'fungus': {'symbol': '🍄', 'name': 'Fungus Garden', 'description': 'Colony food storage'},
    'parasite': {'symbol': '🦠', 'name': 'Parasite', 'description': 'Threatens ant health'},
    'predator': {'symbol': '🐍', 'name': 'Predator', 'description': 'Hunts ants'},
    'empty': {'symbol': '⬜', 'name': 'Empty Space', 'description': 'Available territory'}
}


class InteractiveGridVisualizer:
    """Handles interactive visualization of the simulation grid using Plotly."""
    
    def __init__(self, grid_size: int):
        """Initialize the interactive grid visualizer.
        
        Args:
            grid_size: Size of the simulation grid (NxN)
        """
        self.grid_size = grid_size
        self.figure_size = min(800, max(400, grid_size * 20))
    
    def create_interactive_grid(self, environment) -> go.Figure:
        """Create a stable grid visualization with emoji symbols only.
        
        Args:
            environment: The simulation environment
            
        Returns:
            Plotly Figure object
        """
        # Create the figure
        fig = go.Figure()
        
        # Collect entity positions and info
        entity_mappings = [
            (environment.plants, '🌿', '#27AE60'),
            (environment.fungi, '🍄', '#8E44AD'),
            (environment.parasites, '🦠', '#E74C3C'),
            (environment.predators, '🐍', '#F39C12'),
            (environment.ants, '🐜', '#FF6B35')  # Ants on top
        ]
        
        for entity_list, emoji, color in entity_mappings:
            if not entity_list:
                continue
                
            x_coords = []
            y_coords = []
            hover_texts = []
            
            for entity in entity_list:
                if hasattr(entity, 'active') and entity.active:
                    x, y = entity.position
                    if 0 <= x < self.grid_size and 0 <= y < self.grid_size:
                        x_coords.append(x)
                        y_coords.append(y)
                        
                        # Enhanced hover text with entity-specific info
                        entity_type = emoji.replace('🐜', 'ant').replace('🌿', 'plant').replace('🍄', 'fungus').replace('🦠', 'parasite').replace('🐍', 'predator')
                        info = ENTITY_INFO[entity_type]
                        extra_info = ""
                        if entity_type == 'ant' and hasattr(entity, 'energy'):
                            extra_info = f"<br>Energy: {entity.energy:.1f}"
                        elif entity_type == 'plant' and hasattr(entity, 'growth_stage'):
                            extra_info = f"<br>Growth: {entity.growth_stage:.1f}"
                        elif entity_type == 'fungus' and hasattr(entity, 'nutrition_value'):
                            extra_info = f"<br>Nutrition: {entity.nutrition_value:.1f}"
                        
                        hover_text = (f"<b>{emoji} {info['name']}</b><br>"
                                    f"Position: ({x}, {y})<br>"
                                    f"{info['description']}{extra_info}")
                        hover_texts.append(hover_text)
            
            if x_coords:  # Only add trace if there are entities
                fig.add_trace(go.Scatter(
                    x=x_coords,
                    y=y_coords,
                    mode='text',  # Only text mode with emojis
                    text=[emoji] * len(x_coords),
                    textfont=dict(size=18),
                    name=f"{emoji} {entity_type.title()}",
                    hovertemplate='%{customdata}<extra></extra>',
                    customdata=hover_texts,
                    showlegend=True,
                    marker=dict(color=color, size=0)  # Invisible marker for legend color
                ))
        
        # Style the figure with absolutely stable positioning
        fig.update_layout(
            title=dict(
                text=f'🐜 Ecosystem - Step {environment.step_count}',
                x=0.5,
                font=dict(size=16, color='#2C3E50')
            ),
            width=550,  # Fixed width
            height=550,  # Fixed height  
            xaxis=dict(
                showgrid=True,
                gridwidth=1,
                gridcolor='#E8E8E8',
                zeroline=False,
                showticklabels=True,
                range=[-0.5, self.grid_size-0.5],
                fixedrange=True,
                constrain='domain',
                dtick=1
            ),
            yaxis=dict(
                showgrid=True,
                gridwidth=1,
                gridcolor='#E8E8E8',
                zeroline=False,
                showticklabels=True,
                range=[-0.5, self.grid_size-0.5],
                scaleanchor="x",
                scaleratio=1,
                fixedrange=True,
                constrain='domain',
                dtick=1
            ),
            plot_bgcolor='white',
            paper_bgcolor='white',
            margin=dict(l=50, r=50, t=60, b=90),
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=-0.18,
                xanchor="center",
                x=0.5,
                bgcolor="rgba(248,249,250,0.9)",
                bordercolor="#DDD",
                borderwidth=1,
                font=dict(size=11)
            ),
            autosize=False,
            # Prevent any dynamic resizing
            dragmode=False
        )
        
        # Add subtle climate indicator
        climate_color = '#3498DB' if environment.current_climate.value == 'rain' else '#E67E22'
        climate_icon = '🌧️' if environment.current_climate.value == 'rain' else '☀️'
        
        fig.add_annotation(
            x=0.02, y=0.98,
            xref='paper', yref='paper',
            text=climate_icon,
            showarrow=False,
            bgcolor=climate_color,
            bordercolor="white",
            borderwidth=1,
            font=dict(color="white", size=16),
            xanchor='left',
            yanchor='top',
            width=35,
            height=35
        )
        
        return fig
    
    def create_entity_legend(self) -> go.Figure:
        """Create a clean entity legend with proper spacing.
        
        Returns:
            Plotly Figure object
        """
        entity_names = ['ant', 'plant', 'fungus', 'parasite', 'predator', 'empty']
        colors = [ENTITY_COLORS[name] for name in entity_names]
        info_list = [ENTITY_INFO[name] for name in entity_names]
        
        # Enhanced descriptions with behaviors
        enhanced_descriptions = {
            'ant': 'Forages plants, creates fungi',
            'plant': 'Food source, climate sensitive',
            'fungus': 'Colony food storage',
            'parasite': 'Infectious threat to ants',
            'predator': 'Hunts ants adaptively',
            'empty': 'Available territory'
        }
        
        # Create enhanced legend figure
        fig = go.Figure()
        
        # Calculate proper spacing
        spacing = 0.8
        start_y = len(entity_names) - 1
        
        for i, (name, color, info) in enumerate(zip(entity_names, colors, info_list)):
            current_y = start_y - (i * spacing)
            
            # Add colored square marker
            fig.add_trace(go.Scatter(
                x=[0.1],
                y=[current_y],
                mode='markers',
                marker=dict(
                    size=20,
                    color=color,
                    line=dict(width=2, color='white'),
                    symbol='square'
                ),
                showlegend=False,
                hoverinfo='none'
            ))
            
            # Entity name and symbol (with proper spacing)
            fig.add_annotation(
                x=0.25, y=current_y + 0.1,
                text=f"<b>{info['symbol']} {info['name']}</b>",
                showarrow=False,
                font=dict(size=12, color='#2C3E50'),
                xanchor='left',
                yanchor='bottom'
            )
            
            # Enhanced description (properly spaced below)
            fig.add_annotation(
                x=0.25, y=current_y - 0.15,
                text=f"<i>{enhanced_descriptions[name]}</i>",
                showarrow=False,
                font=dict(size=10, color='#7F8C8D'),
                xanchor='left',
                yanchor='top'
            )
        
        fig.update_layout(
            title=dict(
                text="🗝️ Entity Guide", 
                font=dict(size=15, color='#2C3E50'),
                x=0.5,
                xanchor='center'
            ),
            xaxis=dict(
                showgrid=False, 
                zeroline=False, 
                showticklabels=False, 
                range=[0, 1]
            ),
            yaxis=dict(
                showgrid=False, 
                zeroline=False, 
                showticklabels=False, 
                range=[-0.5, start_y + 0.5]
            ),
            height=400,
            width=280,
            plot_bgcolor='white',
            paper_bgcolor='white',
            margin=dict(l=15, r=15, t=40, b=15)
        )
        
        return fig


def create_interactive_population_chart(simulation) -> go.Figure:
    """Create interactive population trend charts.
    
    Args:
        simulation: The simulation object
        
    Returns:
        Plotly Figure object
    """
    metrics = simulation.get_metrics()
    
    if not metrics['step']:
        # Create empty state figure
        fig = go.Figure()
        fig.add_annotation(
            x=0.5, y=0.5,
            text="🚀 Run simulation to see population dynamics!<br>Click 'Run Full Simulation' to start",
            showarrow=False,
            font=dict(size=16, color='#7F8C8D'),
            xref='paper', yref='paper'
        )
        fig.update_layout(
            title="📊 Population Trends",
            height=400,
            plot_bgcolor='white',
            paper_bgcolor='white'
        )
        return fig
    
    # Create subplot with secondary y-axis
    fig = make_subplots(
        rows=2, cols=1,
        subplot_titles=('Population Dynamics', 'Food Stock & Climate'),
        vertical_spacing=0.15,
        specs=[[{"secondary_y": False}], [{"secondary_y": True}]]
    )
    
    steps = metrics['step']
    
    # Population trends with enhanced styling
    population_data = [
        ('ant_count', 'Ants', ENTITY_COLORS['ant'], 'circle'),
        ('plant_count', 'Plants', ENTITY_COLORS['plant'], 'square'),
        ('fungus_count', 'Fungi', ENTITY_COLORS['fungus'], 'diamond'),
        ('parasite_count', 'Parasites', ENTITY_COLORS['parasite'], 'triangle-up'),
        ('predator_count', 'Predators', ENTITY_COLORS['predator'], 'star')
    ]
    
    for metric, name, color, symbol in population_data:
        fig.add_trace(
            go.Scatter(
                x=steps,
                y=metrics[metric],
                mode='lines+markers',
                name=name,
                line=dict(color=color, width=3),
                marker=dict(symbol=symbol, size=6),
                hovertemplate=f"<b>{name}</b><br>Step: %{{x}}<br>Count: %{{y}}<extra></extra>"
            ),
            row=1, col=1
        )
    
    # Food stock visualization
    if metrics['food_stock']:
        fig.add_trace(
            go.Scatter(
                x=steps,
                y=metrics['food_stock'],
                mode='lines',
                name='Food Stock',
                line=dict(color='#8E44AD', width=4),
                fill='tonexty',
                fillcolor='rgba(142, 68, 173, 0.3)',
                hovertemplate="<b>Food Stock</b><br>Step: %{x}<br>Amount: %{y:.1f}<extra></extra>"
            ),
            row=2, col=1
        )
        
        # Climate background indicators
        climate_data = metrics['climate']
        for i in range(len(steps) - 1):
            color = '#AED6F1' if climate_data[i] == 'rain' else '#F9E79F'
            fig.add_vrect(
                x0=steps[i], x1=steps[i+1],
                fillcolor=color, opacity=0.3,
                line_width=0,
                row=2, col=1
            )
    
    # Update layout
    fig.update_layout(
        height=600,
        title=dict(
            text="📈 Ecosystem Analytics Dashboard",
            x=0.5,
            font=dict(size=20, color='#2C3E50')
        ),
        plot_bgcolor='white',
        paper_bgcolor='white',
        hovermode='x unified',
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    
    fig.update_xaxes(title_text="Simulation Step", row=2, col=1)
    fig.update_yaxes(title_text="Population Count", row=1, col=1)
    fig.update_yaxes(title_text="Food Stock", row=2, col=1)
    
    return fig


def create_ecosystem_health_gauge(balance_analyzer, simulation) -> go.Figure:
    """Create an interactive ecosystem health gauge.
    
    Args:
        balance_analyzer: The ecosystem balance analyzer
        simulation: The simulation object
        
    Returns:
        Plotly Figure object
    """
    health_metrics = balance_analyzer.analyze_ecosystem_health(simulation.environment)
    overall_health = health_metrics['overall']
    sustainability_score, assessment = balance_analyzer.calculate_sustainability_score(simulation.environment)
    
    # Create gauge chart
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=overall_health * 100,
        domain={'x': [0, 1], 'y': [0.25, 1]},  # Adjusted to leave space at bottom
        title={'text': "🌿 Ecosystem Health Score", 'font': {'size': 14}},
        delta={'reference': 70, 'increasing': {'color': "#2ECC71"}},
        gauge={
            'axis': {'range': [None, 100]},
            'bar': {'color': "#3498DB"},
            'steps': [
                {'range': [0, 25], 'color': "#E74C3C"},
                {'range': [25, 50], 'color': "#E67E22"},
                {'range': [50, 75], 'color': "#F39C12"},
                {'range': [75, 100], 'color': "#2ECC71"}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': 90
            }
        }
    ))
    
    fig.update_layout(
        height=350,  # Increased height to accommodate text
        font={'color': "#2C3E50", 'family': "Arial"},
        paper_bgcolor='white',
        margin=dict(l=10, r=10, t=10, b=60)  # Added bottom margin for text
    )
    
    # Add assessment text with proper positioning
    fig.add_annotation(
        x=0.5, y=0.05,  # Positioned at bottom
        text=f"<b>Assessment:</b><br>{assessment}",
        showarrow=False,
        font=dict(size=11, color='#34495E'),
        xref='paper', yref='paper',
        xanchor='center',
        yanchor='bottom',
        bgcolor='rgba(255, 255, 255, 0.8)',
        bordercolor='#BDC3C7',
        borderwidth=1
    )
    
    return fig


def create_spatial_analysis_heatmap(environment, grid_size: int) -> go.Figure:
    """Create spatial density analysis heatmap.
    
    Args:
        environment: The simulation environment
        grid_size: Size of the grid
        
    Returns:
        Plotly Figure object
    """
    # Create density matrices for each entity type
    entity_types = ['ants', 'plants', 'fungi', 'parasites', 'predators']
    entity_names = ['🐜 Ants', '🌿 Plants', '🍄 Fungi', '🦠 Parasites', '🐍 Predators']
    
    fig = make_subplots(
        rows=2, cols=3,
        subplot_titles=entity_names,
        specs=[[{"type": "heatmap"}, {"type": "heatmap"}, {"type": "heatmap"}],
               [{"type": "heatmap"}, {"type": "heatmap"}, None]]
    )
    
    positions = [(1, 1), (1, 2), (1, 3), (2, 1), (2, 2)]
    
    for i, (entity_type, title) in enumerate(zip(entity_types, entity_names)):
        entities = getattr(environment, entity_type)
        density_grid = np.zeros((grid_size, grid_size))
        
        for entity in entities:
            if hasattr(entity, 'active') and entity.active:
                x, y = entity.position
                if 0 <= x < grid_size and 0 <= y < grid_size:
                    density_grid[x, y] = 1
        
        row, col = positions[i]
        color = ENTITY_COLORS[entity_type[:-1]]  # Remove 's' from plural
        
        fig.add_trace(
            go.Heatmap(
                z=density_grid,
                colorscale=[[0, 'white'], [1, color]],
                showscale=False,
                hovertemplate=f"Position: (%{{x}}, %{{y}})<br>Present: %{{z}}<extra></extra>"
            ),
            row=row, col=col
        )
    
    fig.update_layout(
        title="🗺️ Spatial Distribution Analysis",
        height=500,
        paper_bgcolor='white',
        plot_bgcolor='white'
    )
    
    return fig 