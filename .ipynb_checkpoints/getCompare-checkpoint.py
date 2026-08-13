import os
import numpy as np
import matplotlib.pyplot as plt

pfetSim = [
    "idVg_vd_0p370.txt",
    "idVg_vd_1p480.txt",
    "idVg_vd_0p740.txt",
    "idVg_vd_1p110.txt",
    "idVg_vd_0p000.txt",
    "idVg_vd_1p665.txt"
]

getComp = [
    "idVg_vd_0p370.txt",
    "idVg_vd_1p480.txt",
    "idVg_vd_0p740.txt",
    "idVg_vd_1p110.txt",
    "idVg_vd_0p000.txt",
    "idVg_vd_1p665.txt"
]

getMeas = [
    "idvg_Vd-0p37.csv",
    "idvg_Vd-1p48.csv",
    "idvg_Vd-0p74.csv",
    "idvg_Vd-1p11.csv",
    "idvg_Vd-0p01.csv",
    "idvg_Vd-1p85.csv"
]

compPath = "/home/oliviag/ngspice-skywater-sims/outside_data"
simPath = "/home/oliviag/ngspice-skywater-sims/pfet_mod/l_0p35_w_1p6/vg_sweep"
measPath = "/home/oliviag/Skywater-130nm-77K-Cryogenic-Models/cryo_data/pmos_FET_len_0.35_wid_1.6"

plt.figure(figsize=(8, 6))

for sim_name, comp_name , meas_name in zip(pfetSim, getComp, getMeas):

    sim = np.loadtxt(os.path.join(simPath, sim_name))
    comp = np.loadtxt(os.path.join(compPath, comp_name))
    meas =np.loadtxt(os.path.join(measPath, meas_name), delimiter=',', skiprows=1)

    vd_label = sim_name.replace("idVg_vd_", "").replace(".txt", "")

    # Simulation: VGS = col 0, ID = col 3
    plt.plot(
        np.abs(sim[:, 0]),
        np.abs(sim[:, 3]),
        label=f"Olivia Vd={vd_label}"
    )

    # Comparison: assumes VGS = col 0, ID = col 1
    plt.plot(
        np.abs(comp[:, 0]),
        np.abs(comp[:, 5]),
        '--',
        label=f"Ashish Vd={vd_label}"
    )
    plt.plot(
        np.abs(meas[:,1]),   # VGS column
        np.abs(meas[:,2]),   # ID column
        ':',
        label=f"Meas Vd={vd_label}"
    )

#plt.yscale("log")
plt.xlabel("VGS (V)")
plt.ylabel("ID (A)")
plt.title("PFET Id-Vgs Comparison")
plt.grid(True, which="both")
plt.legend(fontsize=8)
plt.tight_layout()
outfile = "pfet_idvg_comparison.png"
plt.savefig(
    outfile,
    dpi=300,
    bbox_inches="tight"
)

print(f"Saved {outfile}")
plt.close()




