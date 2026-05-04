import matplotlib.pyplot as plt
import numpy as np

import flow_state

#set up the font size for the plots
plt.rcParams.update({'font.size': 12})

alt_meters = np.linspace(0,86000, 500)
alt_km = alt_meters / 1000

#calculate density fo ussa and make an empty array
atm_ussa = flow_state.atmosphere.USSA76()
dens_ussa = np.zeros(len(alt_meters))

#fill in the empty array with the density values from the USSA76 model
for i in range(len(alt_meters)):
    dens_ussa[i] = atm_ussa(alt_meters[i]).dens

# creating the set of subplots
fig, ax = plt.subplots(2, 3, figsize = (11, 8.5), sharey = True)

# set up lists of the subplots
latitudes = [0, 40, -40]

titles = ['Equator ($0^o$)', '($40^o$) North', '($40^o$) South']

# loop through the latitudes and plot the density for each one
for i in range(len(latitudes)):
    current_lat = latitudes[i]

    model_jan = flow_state.atmosphere.CIRA86(latitude = current_lat, month = 1)
    model_jul = flow_state.atmosphere.CIRA86(latitude = current_lat, month = 7)

    dens_jan = np.zeros(len(alt_meters))
    dens_jul = np.zeros(len(alt_meters))

    for j in range(len(alt_meters)):
        dens_jan[j] = model_jan(alt_meters[j]).dens
        dens_jul[j] = model_jul(alt_meters[j]).dens

    err_jan = ((dens_jan - dens_ussa) / dens_ussa) *100
    err_jul = ((dens_jul - dens_ussa) / dens_ussa) *100

    top_plot = ax[0, i]
    top_plot.plot(dens_ussa, alt_km, 'k:', label = 'USSA76')
    top_plot.plot(dens_jan, alt_km, 'b-', label = 'CIRA86 (Jan)')
    top_plot.plot(dens_jul, alt_km, 'r--', label = 'CIRA86 (Jul)')

    top_plot.set_title(titles[i])
    top_plot.set_xscale('log')
    top_plot.set_xlabel('ρ (kg/m³)')
    top_plot.set_ylim(0, 100)
    top_plot.set_xlim(1e-6, 10)
    top_plot.grid(True, linestyle = ':')

    bot_plot = ax[1, i]
    bot_plot.plot(err_jan, alt_km, 'b-')
    bot_plot.plot(err_jul, alt_km, 'r--')

    bot_plot.set_xlim(-40, 40)
    bot_plot.set_xticks(np.arange(-40, 41, 10))
    bot_plot.set_xlabel('ε (%) Relative to USSA76')
    bot_plot.grid(True, linestyle = ':')

    top_plot.legend(loc = 'best')

    if i == 0:
        top_plot.set_ylabel('Altitude (km)')
        bot_plot.set_ylabel('Altitude (km)')


plt.tight_layout()
plt.savefig('atmosphere_density_comparison.png', dpi = 300)
plt.show()

