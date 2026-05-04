import matplotlib.pyplot as plt
import numpy as np

import flow_state

# Set parameters
L_ref = 1.0  # Reference length in meters

# Function to calculate viscosity
def sutherland_mu(T):
    mu_ref = 1.716e-5  # Reference viscosity in kg/(m*s)
    T_ref = 273.15   # Reference temperature in K
    S = 110.4      # Sutherland's constant in K

    # The standard Sutherland theoretical formula
    return mu_ref * (T / T_ref)**1.5 * ((T_ref + S) / (T + S))


# Load Data

traj = np.loadtxt('trajectory_digitized_hifire_1_no_confidence_band.dat', skiprows=3)
time = traj[:, 0]
mach = traj[:, 2]
alt_m = traj[:, 1] * 1000  # convert km to m
vel_ms = traj[:, 3] * 1000  # convert km/s to m/s

# Setup Subplots

fig, ax = plt.subplots(2, 3, figsize=(11, 8.5), sharex=True)

latitudes = [0, 40, -40]
titles = ['Equator ($0^o$)', '($40^o$) North', '($40^o$) South']


# Calculate USSA76 (Independent of Latitude)

atm_ussa = flow_state.atmosphere.USSA76()
re_ussa = np.zeros(len(time))

# Basic for-loop with an if-statement checking altitude
for i in range(len(time)):
    if alt_m[i] <= 86000:
        state_ussa = atm_ussa(alt_m[i])
        visc_ussa = sutherland_mu(state_ussa.temp)
        re_ussa[i] = (state_ussa.dens * vel_ms[i] * L_ref) / visc_ussa
    else:
        re_ussa[i] = np.nan


# loop over latitudes for CIRA86
for j in range(len(latitudes)):
    current_lat = latitudes[j]
    current_title = titles[j]

    # Initialize CIRA86 models for current latitude
    model_jan = flow_state.atmosphere.CIRA86(latitude=current_lat, month=1)
    model_jul = flow_state.atmosphere.CIRA86(latitude=current_lat, month=7)

    re_jan = np.zeros(len(time))
    re_jul = np.zeros(len(time))

    for i in range(len(time)):
        if alt_m[i] <= 86000:
            state_jan = model_jan(alt_m[i])
            state_jul = model_jul(alt_m[i])

            visc_jan = sutherland_mu(state_jan.temp)
            visc_jul = sutherland_mu(state_jul.temp)

            re_jan[i] = (state_jan.dens * vel_ms[i] * L_ref) / visc_jan
            re_jul[i] = (state_jul.dens * vel_ms[i] * L_ref) / visc_jul
        else:
            re_jan[i] = np.nan
            re_jul[i] = np.nan

    err_jan = ((re_jan - re_ussa) / re_ussa) * 100
    err_jul = ((re_jul - re_ussa) / re_ussa) * 100

    # Plotting Top Row (Reynolds Numbers)

    top_plot = ax[0, j]
    top_plot.plot(time, re_ussa, 'k:', linewidth=2.5, label='USSA76')
    top_plot.plot(time, re_jan, 'b-', linewidth=2, label='CIRA86 Jan')
    top_plot.plot(time, re_jul, 'r--', linewidth=2, label='CIRA86 Jul')

    top_plot.set_title(current_title)
    top_plot.set_yscale('log')
    top_plot.set_ylim(1e2, 1e8)
    top_plot.grid(True, which='both', linestyle=':', alpha=0.6)
    top_plot.legend(loc='best', fontsize=11)


    # Plotting Bottom Row (Percent Error)

    bot_plot = ax[1, j]

    bot_plot.plot(time, err_jan, 'b-', linewidth=2, label='Jan Error')
    bot_plot.plot(time, err_jul, 'r--', linewidth=2, label='Jul Error')

    bot_plot.set_xlabel('Time (s)')
    bot_plot.set_xlim(left=0)
    bot_plot.set_ylim(-30, 30)
    bot_plot.grid(True, linestyle=':', alpha=0.6)

    # Only set Y-axis labels on the far-left plots
    if j == 0:
        top_plot.set_ylabel('Reynolds Number')
        bot_plot.set_ylabel('Percent Error (%) Relative to USSA76')

plt.tight_layout()
plt.savefig('reynolds_number_comparison.png', dpi=300)
plt.show()
