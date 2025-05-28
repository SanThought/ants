from setuptools import setup, find_packages

setup(
    name="ant_colony_sim",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "streamlit>=1.28.0",
        "numpy>=1.24.0",
        "pydantic>=2.0.0",
        "pytest>=7.0.0",
        "pyyaml>=6.0.0",
        "black>=23.0.0",
        "ruff>=0.1.0",
        "pre-commit>=3.0.0",
        "pandas>=2.0.0"
    ]
) 