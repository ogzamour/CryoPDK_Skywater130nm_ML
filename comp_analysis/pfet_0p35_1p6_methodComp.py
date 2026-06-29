import os
import numpy as np
import matplotlib.pyplot as plt

simVG = [
    "idVg_vd_0p000.txt",
    #"idVg_vd_0p010.txt",
    "idVg_vd_0p370.txt",
    "idVg_vd_1p480.txt",
    "idVg_vd_0p740.txt",
    "idVg_vd_1p110.txt",
    "idVg_vd_1p665.txt",
    #"idVg_vd_1p850.txt"
]


measVG = [
    "idvg_Vd-0p01.csv",
    "idvg_Vd-0p37.csv",
    "idvg_Vd-1p48.csv",
    "idvg_Vd-0p74.csv",
    "idvg_Vd-1p11.csv",
    "idvg_Vd-1p85.csv"
]



compVG = [
    "idVg_vd_0p000.txt",
    "idVg_vd_0p370.txt",
    "idVg_vd_0p740.txt",
    "idVg_vd_1p110.txt",
    "idVg_vd_1p480.txt",
    "idVg_vd_1p665.txt"
]
    
compPath = "/home/oliviag/ngspice-skywater-sims/outside_data"
simPath = "/home/oliviag/ngspice-skywater-sims/pfet_mod/l_0p35_w_1p6/"
measPath = "/home/oliviag/Skywater-130nm-77K-Cryogenic-Models/cryo_data/pmos_FET_len_0.35_wid_1.6"

plt.figure(figsize=(8, 6))


for simFile, measFile, compFile in zip(simVG, measVG, compVG):
    p_s = os.path.join(simPath, "vg_sweep/", simFile)
    p_m = os.path.join(measPath, measFile)
    p_c = os.path.join(compPath, compFile)
    simData = np.loadtxt(p_s)
    measData =np.loadtxt(p_m, delimiter=',', skiprows=1)
    compData = np.loadtxt(p_c)
    vdS = np.abs(simData[0,5])
    vdM = np.abs(measData[0,0])
    vdC = np.abs(compData[0,3])
    plt.plot(
        np.abs(simData[:, 0]),
        np.abs(simData[:, 3]),
        label=f"ngSpice Vd={vdS} V"
    )
    plt.plot(
        np.abs(measData[:,1]),   
        np.abs(measData[:,2]),   
        ':',
        label=f"Measured Vd={vdM} V"
    )
    plt.plot(
    np.abs(compData[:, 0]),
    np.abs(compData[:, 5]),
    '--',
    label=f"xSchem Vd={vdC}"
    )

plt.xlabel("Vgs (V)")
plt.ylabel("Id (A)")
plt.title("PFET Id-Vgs Method Comparison (L=0.35um, W=1.6um)")
plt.grid(True, which="both")
plt.legend(fontsize=8)
plt.tight_layout()
outfile = "methodComp_pfet_0p35_1p6.png"
plt.savefig(
    outfile,
    dpi=300,
    bbox_inches="tight"
)
print(f"Saved {outfile}")
plt.close()
    #Id-Vds plotting
'''for simFile, measFile in zip(simVD, measVD):
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
plt.close()'''



