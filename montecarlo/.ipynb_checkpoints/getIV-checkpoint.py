import numpy as np
import matplotlib.pyplot as plt
import os

# VGS sweep 
def getIvVg(runs, runPath):
    steps = np.arange(runs)
    #print(steps)
    plt.figure(figsize=(10,6))
    outputDir = os.path.join(runPath, "allPlots")
    
    for item in steps:
        file = f"{runPath}/run_{item}/vgs_sweep.csv"
        if not os.path.exists(file):
            print(f'{file} not found')
            continue
        data1 = np.loadtxt(file, delimiter=",", skiprows=1)
        vg1 = np.abs(data1[:,2])
        idrain1 = np.abs(data1[:,3]) 
        vd1 = np.abs(data1[0,1])
        plt.plot(vg1, idrain1 * 1e6)
        
    plt.xlim(0, 1.85)                              
    plt.xticks(np.arange(0, 1.9, 0.2))
    
    plt.title(f"NMOS Id–Vgs, Vds = {vd1} V, {runs} simulations")
    plt.xlabel("Vgs (V)")
    plt.ylabel("Id (uA)")
    p = [ "vth0_nom", "u0_nom", "rdsw_nom", "nfactor_nom", "vsat_nom", "eta0_nom", "delta_nom"]
    pString = ", ".join(p)
    plt.text(0.02, 0.96, f"Variations: {pString}", transform=plt.gca().transAxes, verticalalignment='top', fontsize=11)
    plt.grid(True)
    #plt.legend()
        
    #plt.tight_layout()
    #plt.show()
    
    output_png = f"{outputDir}/IvVg_curves_{runs}_simulations.png"
    plt.savefig(output_png, dpi=300)
    plt.close()
    return

#VDS sweep
def getIvVd(runs, runPath):
    dsteps = np.arange(runs)
    plt.figure(figsize=(10,6))
    outputDir = os.path.join(runPath, "allPlots")
    
    for item in dsteps:
        
        file = f"{runPath}/run_{item}/vds_sweep.csv"
        if not os.path.exists(file):
            continue
        DS = np.loadtxt(file, delimiter=",", skiprows=1)
        vd3 = np.abs(DS[:,1])
        id3 = np.abs(DS[:,3]) 
        vg3 = np.abs(DS[0,2])
        plt.plot(vd3, id3 * 1e6)   
    plt.xlim(0, 1.85)                              
    plt.xticks(np.arange(0, 1.9, 0.2))
    plt.title(f" NMOS Id–Vds, Vgs = {vg3} V, {runs} simulations")
    plt.xlabel("Vds (V)")
    plt.ylabel("Id (uA)")
    p = [ "vth0_nom", "u0_nom", "rdsw_nom", "nfactor_nom", "vsat_nom", "eta0_nom", "delta_nom"]
    pString = ", ".join(p)
    plt.text(0.02, 0.96, f"Variations: {pString}", transform=plt.gca().transAxes, verticalalignment='top', fontsize=11)
    plt.grid(True)
    #plt.legend()
    
    #plt.tight_layout()
   # plt.show()
    output_png = f"{outputDir}/IvVd_curves_{runs}_simulations.png"
    plt.savefig(output_png, dpi=300)
    plt.close()
    return


#def visualizeComparison():
    