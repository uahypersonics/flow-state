# Atmosphere Comparison

!!! warning "Under Construction"
    This page is incomplete.

## Atmosphere Model Temperature Comparison

## Atmosphere Model Density Comparison

![Atmosphere model comparison for density](../assets/atmosphere_density_comparison.png)

![Temperature comparison](../assets/atmosphere_models_temp.png)

![CIRA86 latitude grid](../assets/cira86_latitude_grid.png)

## Reproducing These Plots

The figures were generated with:

```bash
python scripts/temp_graph_atmosphere_models.py     # T
python scripts/atmosphere_density_plotter.py       # $\rho$  
python scripts/generate_latitude_grid.py           # CIRA86 latitude schematic
```

## Sample Trajectory Calculation

Sample Trajectory 1: HIFIRE-1 Flight Experiment 2007 (Kimmel)

![Sample Trajectory 1](../assets/reynolds_number_comparison.png)

Sample Trajectory 2


The figures were generated with:

```bash
python scripts/test_trajectory_1_calculation.py
python scripts/stort_trajectory_reynolds_number_comparison.py
```
