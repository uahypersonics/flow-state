#!/usr/bin/env python3
"""
Example: Compute flow state from Mach number, unit Reynolds number,
and freestream temperature.

Inputs:
    Mach number:          8.0
    Unit Reynolds number: 10e6 [1/m]
    Freestream temperature: 55 K
"""

from flow_state import solve
from flow_state.io import summary, write_flow_conditions_dat, write_json

# --------------------------------------------------
# define inputs
# --------------------------------------------------
mach = 8.0          # mach number [-]
re1 = 10e6          # unit reynolds number [1/m]
temp_inf = 55.0     # freestream temperature [K]

# --------------------------------------------------
# solve for flow state
# --------------------------------------------------
state = solve(
    mach=mach,
    re1=re1,
    temp=temp_inf,
)

# --------------------------------------------------
# print summary to terminal
# --------------------------------------------------
print(summary(state))

# --------------------------------------------------
# write results to json file
# --------------------------------------------------
write_json(state, "mach8_re1_conditions.json")

# --------------------------------------------------
# write results to legacy .dat file
# --------------------------------------------------
write_flow_conditions_dat(state, "mach8_re1_conditions.dat")
