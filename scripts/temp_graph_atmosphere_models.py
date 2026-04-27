#create plot and call it plt
import matplotlib.pyplot as plt

#math and arrays nicknamed np
import numpy as np

#import the documents the atmospheric models are in
import flow_state

#set latitudes
latitudes= [0, 40, -40]

#From 0-120000 meters plot 500 points
alt_range = np.linspace(0, 86000, 500)

# Create subplots: 2 rows (temp and error), 3 columns (latitudes)
fig, axs = plt.subplots(2, 3, figsize=(11, 8.5))

for lat in latitudes:
    col = latitudes.index(lat)

    # Call atmospheric models for ONE latitude at a time
    atm_cira_jan = flow_state.atmosphere.CIRA86(latitude=lat, month=1)
    atm_cira_july = flow_state.atmosphere.CIRA86(latitude=lat, month=7)
    atm_ussa = flow_state.atmosphere.USSA76()
    #we already made the xy locations with alt_range we now need to create placeholders for the temp values to filter in through
    temp_cira_jan = np.zeros_like(alt_range)
    temp_cira_july = np.zeros_like(alt_range)
    temp_ussa = np.zeros_like(alt_range)

    #for i (the postion number), alt (each altitude number) cycle through i values for different altitudes
    for i, alt in enumerate(alt_range):
        temp_cira_jan[i] = atm_cira_jan(alt).temp
        temp_cira_july[i] = atm_cira_july(alt).temp
        temp_ussa[i] = atm_ussa(alt).temp

    # Plot temperature in row 0
    axs[0, col].plot(temp_cira_jan, alt_range, label="CIRA86 January", color='blue')
    axs[0, col].plot(temp_cira_july, alt_range, label="CIRA86 July", linestyle='--', color='red')
    axs[0, col].plot(temp_ussa, alt_range, label="USSA76", linestyle='--', color='black')

    axs[0, col].set_xlabel("T (K)", fontsize=12)
    axs[0, col].set_ylabel("Altitude (km)", fontsize=12)
    axs[0, col].set_title(f"{lat}°", fontsize=12)
    if col == 0:
        axs[0, col].legend(fontsize=12)
    axs[0, col].grid(True)
    axs[0, col].set_xlim(left=150)
    axs[0, col].set_ylim(bottom=0)
    axs[0, col].set_yticks([0, 20000, 40000, 60000, 80000])
    axs[0, col].set_yticklabels(['0', '20', '40', '60', '80'], fontsize=12)

    # Compute errors between CIRA86 and USSA76
    error_jan = temp_cira_jan - temp_ussa
    error_july = temp_cira_july - temp_ussa

    # Plot errors in row 1
    axs[1, col].plot(error_jan, alt_range, label="CIRA86 Jan - USSA76", color='blue')
    axs[1, col].plot(error_july, alt_range, label="CIRA86 July - USSA76", linestyle='--', color='red')
    axs[1, col].set_xlabel(r"$\epsilon$ (%) Relative to USSA76", fontsize=12)
    axs[1, col].set_ylabel("Altitude (km)", fontsize=12)
    axs[1, col].set_title(rf"$\epsilon$ - {lat}°", fontsize=12)
    if col == 0:
        axs[1, col].legend(fontsize=12)
    axs[1, col].grid(True)
    axs[1, col].set_xlim(-20, 20)
    axs[1, col].set_yticks([0, 20000, 40000, 60000, 80000])
    axs[1, col].set_yticklabels(['0', '20', '40', '60', '80'], fontsize=12)

plt.tight_layout()
plt.show()
