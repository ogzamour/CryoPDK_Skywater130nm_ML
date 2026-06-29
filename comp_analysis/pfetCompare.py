import os
import numpy as np
import matplotlib.pyplot as plt

simVG = [
    "idVg_vd_0p010.txt",
    "idVg_vd_0p370.txt",
    "idVg_vd_1p480.txt",
    "idVg_vd_0p740.txt",
    "idVg_vd_1p110.txt",
    "idVg_vd_1p850.txt"
]


measVG = [
    "idvg_Vd-0p01.csv",
    "idvg_Vd-0p37.csv",
    "idvg_Vd-1p48.csv",
    "idvg_Vd-0p74.csv",
    "idvg_Vd-1p11.csv",
    "idvg_Vd-1p85.csv"
]

simVD = [
    "idVd_vg_0p370.txt",
    "idVd_vg_0p740.txt",
    "idVd_vg_1p480.txt",
    "idVd_vg_1p110.txt",
    "idVd_vg_1p850.txt"
]
measVD = [
    "idvd_Vg-0p37.csv",
    "idvd_Vg-0p74.csv",
    "idvd_Vg-1p48.csv",
    "idvd_Vg-1p11.csv",
    "idvd_Vg-1p85.csv"
]

sim_devices = [
    "l_0p35_w_1p6",
    "l_0p50_w_0p42",
    "l_2p0_w_5p0",
    "l_8p0_w_0p84",
    "l_8p0_w_5p0",
    "l_0p35_w_0p55",
    "l_0p35_w_5p0",
    "l_0p50_w_0p64",
    "l_4p0_w_7p0",
    "l_8p0_w_1p6"
]

meas_devices = [
    'pmos_FET_len_0.35_wid_1.6',
    'pmos_FET_len_0p5_wid_0p42',
    'pmos_FET_len_2_wid_5',
    'pmos_FET_len_8_wid_0p84',
    'pmos_FET_len_8_wid_5',
    'pmos_FET_len_0p35_wid_0p55',
    'pmos_FET_len_0p35_wid_5',
    'pmos_FET_len_0p5_wid_0p64',   
    'pmos_FET_len_4_wid_7', 
    'pmos_FET_len_8_wid_1p6'
    
]

simPath = "/home/oliviag/ngspice-skywater-sims/pfet_mod/"
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
    plt.title(f"PFET Id-Vgs Comparison {dev_s}")
    plt.grid(True, which="both")
    plt.legend(fontsize=8)
    plt.tight_layout()
    outfile = f"pfetVGS_compare_{dev_s}.png"
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
    plt.title(f"PFET Id-Vds Comparison {dev_s}")
    plt.grid(True, which="both")
    plt.legend(fontsize=8)
    plt.tight_layout()
    outfile = f"pfetVDS_compare_{dev_s}.png"
    plt.savefig(
        outfile,
        dpi=300,
        bbox_inches="tight"
    )
    print(f"Saved {outfile}")
    plt.close()



