import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np

import flow_state

L_ref = 1.0

def sutherland_mu(T):
    return 1.716e-5 * (T / 273.15)**1.5 * (273.15 + 110.4) / (T + 110.4)

traj = np.loadtxt('trajectory_digitized_stort_no_confidence_band.dat', skiprows=3)

time, alt_m, vel_ms = traj[:, 0], traj[:, 1] * 1000, traj[:, 3] * 1000

fig, ax = plt.subplots(2, 3, figsize=(15, 8), sharex=True)

fig.suptitle(f'Stort Reynolds Number vs Time (L = {L_ref} m)',
             fontsize=16, fontweight='bold')

atm_ussa = flow_state.atmosphere.USSA76()

re_ussa = np.array([
    (atm_ussa(alt_m[i]).dens * vel_ms[i] * L_ref) /
    sutherland_mu(atm_ussa(alt_m[i]).temp)
    for i in range(len(time))
])

xmax = int(np.ceil(time.max() / 10) * 10)

for j, (lat, title) in enumerate(zip([0, 40, -40],
                                     ['Equator (0°)', '40° North', '40° South'])):

    model_jan = flow_state.atmosphere.CIRA86(latitude=lat, month=1)
    model_jul = flow_state.atmosphere.CIRA86(latitude=lat, month=7)

    re_jan = np.array([
        (model_jan(alt_m[i]).dens * vel_ms[i] * L_ref) /
        sutherland_mu(model_jan(alt_m[i]).temp)
        for i in range(len(time))
    ])

    re_jul = np.array([
        (model_jul(alt_m[i]).dens * vel_ms[i] * L_ref) /
        sutherland_mu(model_jul(alt_m[i]).temp)
        for i in range(len(time))
    ])

    err_jan = ((re_jan - re_ussa) / re_ussa) * 100
    err_jul = ((re_jul - re_ussa) / re_ussa) * 100

    ax[0, j].plot(time, re_ussa, 'k:', linewidth=2.5, label='USSA76')
    ax[0, j].plot(time, re_jan, 'b-', linewidth=2, label='CIRA86 Jan')
    ax[0, j].plot(time, re_jul, 'r--', linewidth=2, label='CIRA86 Jul')

    ax[0, j].set_title(title)
    ax[0, j].set_yscale('log')
    ax[0, j].set_xlim(0, xmax)
    ax[0, j].set_ylim(1e5, 1e8)
    ax[0, j].grid(True, which='both', linestyle=':', alpha=0.6)
    ax[0, j].legend(loc='best', fontsize=11)
    ax[0, j].yaxis.set_major_locator(ticker.LogLocator(base=10))

    ax[1, j].plot(time, err_jan, 'b-', linewidth=2, label='Jan Error')
    ax[1, j].plot(time, err_jul, 'r--', linewidth=2, label='Jul Error')

    ax[1, j].set_xlabel('Time (s)')
    ax[1, j].set_xlim(0, xmax)
    ax[1, j].set_ylim(-20, 15)
    ax[1, j].grid(True, linestyle=':', alpha=0.6)
    ax[1, j].xaxis.set_major_locator(ticker.MultipleLocator(50))
    ax[1, j].yaxis.set_major_locator(ticker.MultipleLocator(5))

    if j == 0:
        ax[0, j].set_ylabel('Reynolds Number')
        ax[1, j].set_ylabel('Percent Error (%) Relative to USSA76')

plt.tight_layout()

plt.savefig("reynolds_comparison.png", dpi=300, bbox_inches="tight")

plt.show()