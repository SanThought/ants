# 🌿 Leafcutter Colony Ecosystem Simulation

A modular, scientifically-inspired simulation of a leafcutter ant ecosystem featuring dynamic interactions between ants, plants, fungi, parasites, and predators.

## Features

- **Realistic Ecosystem Dynamics**: Plant regeneration, reproductive cycles, and climate events
- **Multiple Species Interactions**: Ants, leaves, fungi, parasites, and predators
- **Adaptive Balance**: Dynamic predator-prey relationships and resource management
- **Interactive Visualization**: Real-time Streamlit interface with adjustable parameters
- **Modular Architecture**: Clean separation of concerns for easy testing and extension

## Installation

1. Clone or download this repository
2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Running the Simulation

```bash
streamlit run app/streamlit_app.py
```

## Parameters Guide

### Basic Parameters
- **Ecosystem Size**: Grid dimensions (NxN)
- **Initial Populations**: Starting numbers for each species
- **Simulation Steps**: Total duration of the simulation
- **Animation Speed**: Delay between frames

### Advanced Parameters
- **Regeneration Rate**: How quickly plants regrow
- **Reproductive Threshold**: Food required for ant reproduction
- **Climate Cycle**: Frequency of weather changes
- **Predator Balance**: Adaptive predator spawn rates

## Project Structure

```
leafcutter-colony/
├─ src/                     # Core simulation logic
│   ├─ models/             # Entity definitions
│   ├─ environment.py      # Grid and spatial logic
│   ├─ simulation.py       # Main simulation engine
│   ├─ balance.py          # Ecological balance functions
│   └─ config.py           # Configuration management
├─ app/                    # User interface
├─ tests/                  # Unit tests
└─ data/                   # Default parameters
```

## Testing

Run the test suite:
```bash
pytest tests/
```

## Development

This project uses:
- **Black** for code formatting
- **Ruff** for linting
- **Pydantic** for configuration validation
- **pytest** for testing

Set up pre-commit hooks:
```bash
pre-commit install
``` 