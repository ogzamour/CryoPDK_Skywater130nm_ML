import numpy as np
import matplotlib.pyplot as plt
import os

# VGS sweep 
def getIvVg(runs, path, t, p):
    steps = np.arange(runs)
    #print(steps)
    plt.figure(figsize=(10,6))
    
    
    for item in steps:
        #file = f"/home/oliviag/ngspice-skywater-sims/sim_data_vd/{item}_mosfetVGS_MC_all.csv"
        #file = f"/home/oliviag/ngspice-skywater-sims/sim_data/run_{item}.csv"
        file = f"{path}/output{item}.csv"
        if not os.path.exists(file):
            continue
        data1 = np.loadtxt(file, delimiter=",", skiprows=1)
        
        
       
        vg1 = data1[:,0]
        idrain1 = -data1[:,3]  
        vth1 = data1[1,4] #changing param
        vd1 = data1[0,2]
        #plt.figure(figsize=(10,6))
        plt.plot(vg1, idrain1 * 1e6)
        #print(f"done: {item}")
        
    plt.xlim(0, 1.85)                              
    plt.xticks(np.arange(0, 1.9, 0.2))
    
    plt.title(f"NMOS Id–Vgs, Vds = {vd1} V, {runs} simulations")
    plt.xlabel("Vgs (V)")
    plt.ylabel("Id (uA)")
    pString = ", ".join(p)
    plt.text(0.02, 0.96, f"Variations: {pString}", transform=plt.gca().transAxes, verticalalignment='top', fontsize=11)
    #plt.legend()
    plt.grid(True)
        
    plt.tight_layout()
    plt.show()
    
    output_png = f"/home/oliviag/ngspice-skywater-sims/mc_curves/plot_{t}_vgs.png"
    plt.savefig(output_png, dpi=300)
    plt.close()
    return

#VDS sweep
def getIvVd(runs, path, t, p):
    dsteps = np.arange(runs)
    #print(steps)
    plt.figure(figsize=(10,6))
    
    
    for item in dsteps:
        #file = f"/home/oliviag/ngspice-skywater-sims/sim_data_vd/{item}_mosfetVGS_MC_all.csv"
        #file = f"/home/oliviag/ngspice-skywater-sims/sim_data/run_{item}.csv"
        file = f"{path}/output{item}.csv"
        if not os.path.exists(file):
            continue
        DS = np.loadtxt(file, delimiter=",", skiprows=1)
    
        
        
        vd3 = DS[:,0]
        id3 = -DS[:,3] 
        #vth2 = DS[1,4]
        vg3 = DS[0,1]
        
        
        plt.plot(vd3, id3 * 1e6)   
    plt.xlim(0, 1.85)                              
    plt.xticks(np.arange(0, 1.9, 0.2))
    plt.title(f" NMOS Id–Vds, Vgs = {vg3} V, {runs} simulations")
    plt.xlabel("Vds (V)")
    plt.ylabel("Id (uA)")
    pString = ", ".join(p)
    plt.text(0.02, 0.96, f"Variations: {pString}", transform=plt.gca().transAxes, verticalalignment='top', fontsize=11)
    #plt.legend()
    plt.grid(True)
    
    plt.tight_layout()
    plt.show()
    output_png = f"/home/oliviag/ngspice-skywater-sims/mc_curves/plot_{t}_vds.png"
    plt.savefig(output_png, dpi=300)
    plt.close()
    return


#def visualizeComparison():
    