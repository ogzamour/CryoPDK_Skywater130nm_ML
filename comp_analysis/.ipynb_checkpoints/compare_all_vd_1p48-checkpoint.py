import os
import numpy as np
import matplotlib.pyplot as plt

pfetSim = "/home/oliviag/ngspice-skywater-sims/outside_data/simulated_nmos.txt"

getComp = "/home/oliviag/ngspice-skywater-sims/outside_data/nmos_1p6.txt"

getHspice = "/home/oliviag/ngspice-skywater-sims/outside_data/hspice.csv"

getMeas = "/home/oliviag/Skywater-130nm-77K-Cryogenic-Models/cryo_data/nmos_FET_len_0p15_wid_1p6/idvg_Vd1p48.csv"

#compPath = "/home/oliviag/ngspice-skywater-sims/outside_data"
#simPath = "/home/oliviag/ngspice-skywater-sims/pfet_mod/l_0p35_w_1p6/vg_sweep"
#measPath = "/home/oliviag/Skywater-130nm-77K-Cryogenic-Models/cryo_data/pmos_FET_len_0.35_wid_1.6/"idvg_Vd-1p48.csv"

plt.figure(figsize=(8, 6))



sim = np.loadtxt(pfetSim)
comp = np.loadtxt(getComp)
meas =np.loadtxt(getMeas, delimiter=',', skiprows=1)#63
hspice = np.loadtxt(getHspice, delimiter=',', skiprows=1)

vd_label = 1.48

# Simulation: VGS = col 0, ID = col 3
plt.plot(
    np.abs(sim[:, 0]),
    np.abs(sim[:, 3]),
    label=f"Ngspice Vd={vd_label}"
)

# Comparison: assumes VGS = col 0, ID = col 1

plt.plot(
    np.abs(hspice[:, 0]),
    np.abs(hspice[:, 2]),
    '-.',
    label=f"Hspice Vd={vd_label}"
)
plt.plot(
    np.abs(comp[:, 0]),
    np.abs(comp[:, 1]),
    '--',
    label=f"xSchem Vd={vd_label}"
)
plt.plot(
    np.abs(meas[:,1]),   # VGS column
    np.abs(meas[:,2]),   # ID column
    ':',
    label=f"Measured Vd={vd_label}"
)

#plt.yscale("log")
plt.xlabel("VGS (V)")
plt.ylabel("ID (A)")
plt.title("Id-Vgs Comparison NFET L=0.15um W=1.6um")
plt.grid(True, which="both")
plt.legend(fontsize=8)
plt.tight_layout()
outfile = "meathodComp.png"
plt.savefig(
    outfile,
    dpi=300,
    bbox_inches="tight"
)

print(f"Saved {outfile}")
plt.close()




