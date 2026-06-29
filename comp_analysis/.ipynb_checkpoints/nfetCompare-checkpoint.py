import os
import numpy as np
import matplotlib.pyplot as plt

simVG = [
    "idVg_vd_0p370.txt",
    "idVg_vd_1p480.txt",
    "idVg_vd_0p740.txt",
    "idVg_vd_1p110.txt",
    "idVg_vd_0p010.txt",
    "idVg_vd_1p850.txt"
]


measVG = [
    "idvg_Vd0p37.csv",
    "idvg_Vd1p48.csv",
    "idvg_Vd0p74.csv",
    "idvg_Vd1p11.csv",
    "idvg_Vd0p01.csv",
    "idvg_Vd1p85.csv"
]

simVD = [
    "idVd_vg_0p370.txt",
    "idVd_vg_1p480.txt",
    "idVd_vg_0p740.txt",
    "idVd_vg_1p110.txt",
    "idVd_vg_1p850.txt"
]
measVD = [
    "idvd_Vg0p37.csv",
    "idvd_Vg1p48.csv",
    "idvd_Vg0p74.csv",
    "idvd_Vg1p11.csv",
    "idvd_Vg1p85.csv"
]

sim_devices = [
    "l_0p15_w_1p6",
    "l_0p19_w_7p0",
    "l_0p25_w_1p6",
    "l_1p0_w_1p6",
    "l_1p0_w_3p0",
    "l_8p0_w_1p6",
    "l_20p0_w_0p64",
    "l_100p0_w_100p0"
]

meas_devices = [
    'nmos_FET_len_0p15_wid_1p6', 
    'nmos_FET_len_0p19_wid_7',
    'nmos_FET_len_0p25_wid_1p6', 
    'nmos_FET_len_1_wid_1p6', 
    'nmos_FET_len_1_wid_3', 
    'nmos_FET_len_8_wid_1.6', 
    'nmos_FET_len_20_wid_0p64', 
    'nmos_FET_len_100_wid_100'
]

#compPath = "/home/oliviag/ngspice-skywater-sims/outside_data"
#simPath = "/home/oliviag/ngspice-skywater-sims/nfet_mod/l_100p0_w_100p0/vg_sweep"
#simPathVD = "/home/oliviag/ngspice-skywater-sims/nfet_mod/l_100p0_w_100p0/vd_sweep"
#measPath = "/home/oliviag/Skywater-130nm-77K-Cryogenic-Models/cryo_data/nmos_FET_len_100_wid_100"

simPath = "/home/oliviag/ngspice-skywater-sims/nfet_mod/"
#simPathVD = "/home/oliviag/ngspice-skywater-sims/nfet_mod/"
measPath = "/home/oliviag/Skywater-130nm-77K-Cryogenic-Models/cryo_data/"

plt.figure(figsize=(8, 6))

for dev_s, dev_m in zip(sim_devices, meas_devices):
    pSim = os.path.join(simPath, dev_s)
    pMeas = os.path.join(measPath, dev_m)
    for simFile, measFile in zip(simVG, measVG):
        p_s = os.path.join(pSim, "vg_sweep/", simFile)
        p_m = os.path.join(pMeas, measFile)
        simData = np.loadtxt(p_s)
        measData =np.loadtxt(p_m, delimiter=',', skiprows=1)
        vd = np.abs(measData[0,0])
        plt.plot(
            np.abs(simData[:, 0]),
            np.abs(simData[:, 3]),
            label=f"ngSpice Vd={vd} V"
        )
        plt.plot(
            np.abs(measData[:,1]),   
            np.abs(measData[:,2]),   
            ':',
            label=f"Measured Vd={vd} V"
        )

    plt.xlabel("Vgs (V)")
    plt.ylabel("Id (A)")
    plt.title(f"NFET Id-Vgs Comparison {dev_s}")
    plt.grid(True, which="both")
    plt.legend(fontsize=8)
    plt.tight_layout()
    outfile = f"nfetVGS_compare_{dev_s}.png"
    plt.savefig(
        outfile,
        dpi=300,
        bbox_inches="tight"
    )
    print(f"Saved {outfile}")
    plt.close()
    #Id-Vds plotting
    for simFile, measFile in zip(simVD, measVD):
        p_s = os.path.join(pSim, "vd_sweep/", simFile)
        p_m = os.path.join(pMeas, measFile)
        simData = np.loadtxt(p_s)
        measData =np.loadtxt(p_m, delimiter=',', skiprows=1)
        vg = np.abs(measData[0,1])
        plt.plot(
            np.abs(simData[:, 0]),
            np.abs(simData[:, 3]),
            label=f"ngSpice Vg={vg} V"
        )
        plt.plot(
            np.abs(measData[:,0]),   
            np.abs(measData[:,2]),   
            ':',
            label=f"Measured Vg={vg} V"
        )

    plt.xlabel("Vds (V)")
    plt.ylabel("Id (A)")
    plt.title(f"NFET Id-Vds Comparison {dev_s}")
    plt.grid(True, which="both")
    plt.legend(fontsize=8)
    plt.tight_layout()
    outfile = f"nfetVDS_compare_{dev_s}.png"
    plt.savefig(
        outfile,
        dpi=300,
        bbox_inches="tight"
    )
    print(f"Saved {outfile}")
    plt.close()



'''
#plt.figure(figsize=(8, 6))
#for sim_name, comp_name , meas_name in zip(pfetSim, getComp, getMeas):
for sim_name, meas_name in zip(simVD, measVD):

    sim = np.loadtxt(os.path.join(simPathVD, sim_name))
    #comp = np.loadtxt(os.path.join(compPath, comp_name))
    meas =np.loadtxt(os.path.join(measPath, meas_name), delimiter=',', skiprows=1)

    #vd_label = sim_name.replace("idVg_vd_", "").replace(".txt", "")
    vg = sim[0,1]
    # Simulation: VGS = col 0, ID = col 3
    plt.plot(
        np.abs(sim[:, 0]),
        np.abs(sim[:, 3]),
        label=f"Olivia Vg={vg}"
    )
    
    plt.plot(
        np.abs(meas[:,0]),   # VGS column
        np.abs(meas[:,2]),   # ID column
        ':',
        label=f"Meas Vg={vg}"
    )

#plt.yscale("log")
plt.xlabel("Vds (V)")
plt.ylabel("Id (A)")
plt.title("NFET Id-Vds Comparison (L=100um W=100um)")
plt.grid(True, which="both")
plt.legend(fontsize=8)
plt.tight_layout()
outfile2 = "nfetVDS_compare_100_100.png"
plt.savefig(
    outfile2,
    dpi=300,
    bbox_inches="tight"
)

print(f"Saved {outfile2}")
plt.close()'''





'''getComp = [
    "idVg_vd_0p370.txt",
    "idVg_vd_1p480.txt",
    "idVg_vd_0p740.txt",
    "idVg_vd_1p110.txt",
    "idVg_vd_0p000.txt",
    "idVg_vd_1p665.txt"
]'''
    
'''plt.plot(
        np.abs(comp[:, 0]),
        np.abs(comp[:, 5]),
        '--',
        label=f"Ashish Vd={vd_label}"
    )'''