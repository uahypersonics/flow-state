"""Gas models for compressible flow calculations.

Currently implemented:
    - PerfectGas: calorically perfect gas (constant gamma, r_gas)
    - ParkAir: high-temperature air with vibrational excitation
    - EquilibriumAir: equilibrium air with dissociation effects

Model selection guide:
    - T < 800 K: PerfectGas (simplest, fastest)
    - 500 K < T < 2500 K: ParkAir (vibrational excitation)
    - 2000 K < T < 9000 K: EquilibriumAir (dissociation)
"""

from flow_state.gas.equilibrium import EquilibriumAir
from flow_state.gas.park import ParkAir
from flow_state.gas.perfect import PerfectGas
from flow_state.gas.registry import available_gases, get_gas

__all__ = ["PerfectGas", "ParkAir", "EquilibriumAir", "get_gas", "available_gases"]
