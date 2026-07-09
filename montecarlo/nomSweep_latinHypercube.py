import numpy as np
import matplotlib.pyplot as plt
import subprocess
import csv
import os
from datetime import datetime
from pathlib import Path
import time
from nominal_lib import *
from getCSV import makeCSV
from getIV import getIvVd, getIvVg
from scipy.stats import qmc
N_RUNS = 10000
#SPICE_FILE = "nfet_base.spice"
PARENT_DIR = Path.home() / "ngspice-skywater-sims/montecarlo/mc_output_lhc"
desired_device = 0
#//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
device_library = [("nmos_FET_len_0p15_wid_1p6", model_devs[0],'n', '0'),
           ("nmos_FET_len_0p19_wid_7", model_devs[1],'n', '1'),
           ("nmos_FET_len_0p25_wid_1p6", model_devs[2],'n','2'),
           ('nmos_FET_len_1_wid_1p6', model_devs[3],'n','3'),
           ('nmos_FET_len_1_wid_3', model_devs[4],'n', '4'),
           ('nmos_FET_len_8_wid_1p6', model_devs[5],'n', '5'),
           ('nmos_FET_len_20_wid_0p64', model_devs[6],'n','6'),
           ('nmos_FET_len_100_wid_100', model_devs[7],'n','7'),
           ('pmos_FET_len_8_wid_0p84', model_devs[8],'p','8'),
           ('pmos_FET_len_0p35_wid_1p6', model_devs[9],'p','0'),
           ('pmos_FET_len_0p5_wid_0p42', model_devs[10],'p','7'),
           ('pmos_FET_len_0p35_wid_0p55', model_devs[11],'p','5'),
           ('pmos_FET_len_0p5_wid_0p64', model_devs[12],'p','4'),
           ('pmos_FET_len_0p35_wid_5', model_devs[13],'p','9'),
           ('pmos_FET_len_2_wid_5', model_devs[14],'p','11'),
           ('pmos_FET_len_4_wid_7', model_devs[15],'p','2'),
           ('pmos_FET_len_8_wid_1p6', model_devs[16],'p','6'),
           ('pmos_FET_len_8_wid_5', model_devs[17],'p','1')
]

#//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
def getHypercube(num_samples, runDir, p):
    num_vars = 7 # e.g., Width (W) and Length (L)
    #p = np.loadtxt(os.path.join(dev_dir, "model_parameters.txt")) #original parameters for setting bounds
    
    sampler = qmc.LatinHypercube(d=num_vars)
    sample_matrix = sampler.random(n=num_samples)

    b1 = 0.9 * p
    b2 = 1.1 * p
    floor = np.minimum(b1, b2)   # Forces the truest minimum
    ceiling = np.maximum(b1, b2)

    scaled_matrix = qmc.scale(sample_matrix, floor, ceiling)
    
    # Export to a text file for ngspice to read
    np.savetxt(os.path.join(runDir,'lhs_parameters.txt'), scaled_matrix, fmt='%.16e')
   
    return
#//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
def lhcVisual(runDir):
    labels = ["vth0", "vsat", "rdsw", "u0", "nfactor", "eta0", "delta"]
    
    file_path = os.path.join(runDir, 'lhs_parameters.txt')
    if not os.path.exists(file_path):
        print(f"Error: {file_path} not found.")
        return
        
    matrix = np.loadtxt(file_path)
    num_samples, num_vars = matrix.shape
    fig, axes = plt.subplots(num_vars, num_vars, figsize=(14, 14), sharex='col')
    colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b', '#e377c2']
    
    for i in range(num_vars):
        for j in range(num_vars):
            ax = axes[i, j]       
            #corner grid layout
            if j > i:
                ax.set_visible(False)
                continue    
            #histogram on diagonal
            if i == j:
                ax.hist(matrix[:, i], bins=12, color=colors[i], edgecolor='white', alpha=0.8)
                ax.tick_params(axis='y', which='both', left=False, labelleft=False)
            #plotting multivariable scatter representations
            else:
                ax.scatter(matrix[:, j], matrix[:, i], color='#555555', alpha=0.5, edgecolors='none', s=20)
                ax.set_ylim(matrix[:, i].min() * 0.98, matrix[:, i].max() * 1.02)
            #boundaries and layout frames
            ax.set_xlim(matrix[:, j].min() * 0.98, matrix[:, j].max() * 1.02)
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            #format peripheral label text on edge borders only
            if j == 0 and i != 0:
                ax.set_ylabel(labels[i], fontsize=11, fontweight='bold')
            if i == num_vars - 1:
                ax.set_xlabel(labels[j], fontsize=11, fontweight='bold')
                ax.tick_params(axis='x', labelrotation=45)
    #saving
    fig.tight_layout()
    outdir = os.path.join(runDir, "allPlots")
    outfile = os.path.join(outdir, "LHC_Sampling_Visualization.png")
    fig.savefig(outfile, dpi=300, bbox_inches="tight")
    
    print(f"Saved {outfile}")
    plt.close(fig)
    return

#//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
def deviceTemplate(dev_dir, dev_param, devType):
    if devType == 'p':
        biasV = -1.48
    else:
        biasV = 1.48
    home = str(Path.home())
    #nfet_meas = 
    
    device_cmd = f"""* NMOS sweep (Sky130) 


{dev_param} nf=1 ad='floor((nf+1)/2) * w/nf * 0.29' as='floor((nf+2)/2) * w/nf * 0.29' pd='2 * floor((nf+1)/2) * (w/nf + 0.29)' ps='2 * floor((nf+2)/2) * (w/nf + 0.29)' nrd='0.29 / w' nrs='0.29 / w' sa=0 sb=0 sd=0 

.lib "{home}/skywater130nm/volare/sky130/versions/a918dc7c8e474a99b68c85eb3546b4ed91fe9e7b/sky130A/libs.tech/ngspice/sky130.lib.spice" tt_77k

Vgs gate GND {biasV}
Vds VDD GND {biasV}
.temp -196.15


"""
    file = 'mc_template.spice'
    outFile = os.path.join(dev_dir, file)
    if not os.path.exists(outFile):
        with open(outFile, "w+") as f:
            f.write(device_cmd)
            f.flush()
        
    return outFile
#//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
'''start_time = time.perf_counter()
folder = datetime.now().strftime(f"{N_RUNS}_runs_data_%Y-%m-%d_%H-%M-%S")

#device setup
device = device_library[desired_device]
deviceName = device[0]
circuit = device[1]
fet = device[2]
nom_params_key = f"{fet}fet_mod_{device[3]}"
modP = mods_list.get(nom_params_key, {})

#directroy + template setup
dev_dir = PARENT_DIR / deviceName
run_dir = dev_dir / folder
run_dir.mkdir(parents=True, exist_ok=True)
print(run_dir)
plotDir = run_dir / "allPlots"
plotDir.mkdir(parents=True, exist_ok=True)
deviceTemplate(dev_dir, circuit, fet)
SPICE_FILE = os.path.join(dev_dir, "mc_template.spice")

#boundary setup and LHC run
param_init = np.array([
    float(modP["vth0_nom"]), 
    float(modP["vsat_nom"]), 
    float(modP["rdsw_nom"]), 
    float(modP["u0_nom"]), 
    float(modP["nfactor_nom"]), 
    float(modP["eta0_nom"]), 
    float(modP["delta_nom"])
])
getHypercube(N_RUNS, run_dir, param_init)
lhcVisual(run_dir)
lhs_runs = np.loadtxt(os.path.join(run_dir, "lhs_parameters.txt"))
#vth0_v, u0_v, rdsw_v, nfactor_v, vsat_v, eta0_v, delta_v = lhs_runs.T

#netlist setup for each LHC sweep
control_lines = [
    ".control",
    "set noaskquit",
    "set filetype=csv",
    "run",

]
for idx, run in enumerate(lhs_runs):
    v_vth0, v_u0, v_rdsw, v_nfactor, v_vsat, v_eta0, v_delta = run
    runPath = Path(run_dir)
    outdir = f"run_{idx}"
    outPath = runPath / outdir
    outPath.mkdir(parents=True, exist_ok=True)
    vds_file = outPath / "vds_sweep.dat"
    #vgs_single_file = outPath / "vgs_sweep_0p01_vd.csv"
    vgs_file = outPath / "vgs_sweep.dat"
    p_file = outPath / "new_params.txt"

    if fet == 'n':
        control_lines.extend([
    f'echo " MONTE CARLO RUN: {idx}"',
    # Dynamically update the specific instance parameters
    f'alterparam vth0_nom = {v_vth0}',
    f'alterparam u0_nom = {v_u0}',
    f'alterparam rdsw_nom = {v_rdsw}',
    f'alterparam nfactor_nom = {v_nfactor}',
    f'alterparam vsat_nom = {v_vsat}',
    f'alterparam eta0_nom = {v_eta0}',
    f'alterparam delta_nom = {v_delta}',
    'reset',
    
    #'dc Vds 0 1.85 0.01 Vgs 0 1.85 0.185',
    'alter Vgs 1.48',
    'dc Vds 0 1.85 0.01',
    #f'show m.xm1.msky130_fd_pr__nfet_01v8_lvt | tee {p_file} > /dev/null',
    #f'wrdata {p_file} vth0 u0 rdsw nfactor vsat eta0 delta',
    f'let nom_vth0    = {v_vth0}',
    f'let nom_u0      = {v_u0}',
    f'let nom_rdsw    = {v_rdsw}',
    f'let nom_nfactor = {v_nfactor}',
    f'let nom_vsat    = {v_vsat}',
    f'let nom_eta0    = {v_eta0}',
    f'let nom_delta   = {v_delta}',
    f'let run_num     = {idx}',
    'let ax_id0 = -vds#branch',
    #'set wr_vecnames',
    'set wr_singlescale',
    f'wrdata {vds_file} vdd gate ax_id0 nom_vth0 nom_u0 nom_rdsw nom_nfactor nom_vsat nom_eta0 nom_delta',
    
    #'dc Vgs 0 1.85 0.01 Vds 0.01 0.01 1',
    #f'let nom_vth0    = {v_vth0} * (v(gate)*0 + 1)',
    #f'let nom_u0      = {v_u0} * (v(gate)*0 + 1)',
    #f'let nom_rdsw    = {v_rdsw} * (v(gate)*0 + 1)',
    #f'let nom_nfactor = {v_nfactor} * (v(gate)*0 + 1)',
    #f'let nom_vsat    = {v_vsat} * (v(gate)*0 + 1)',
    #f'let nom_eta0    = {v_eta0} * (v(gate)*0 + 1)',
    #f'let nom_delta   = {v_delta} * (v(gate)*0 + 1)',
    #f'let run_num     = {idx} * (v(gate)*0 + 1)',
    #'let ax_id1 = -vds#branch',
    #f'wrdata {vgs_single_file} vdd gate ax_id1 nom_vth0 nom_u0 nom_rdsw nom_nfactor nom_vsat nom_eta0 nom_delta',
    
    #'dc Vgs 0 1.85 0.01 Vds 0 1.85 0.185',
    'dc Vgs 0 1.85 0.01',
    f'let nom_vth0    = {v_vth0}',
    f'let nom_u0      = {v_u0}',
    f'let nom_rdsw    = {v_rdsw}',
    f'let nom_nfactor = {v_nfactor}',
    f'let nom_vsat    = {v_vsat}',
    f'let nom_eta0    = {v_eta0}',
    f'let nom_delta   = {v_delta}',
    f'let run_num     = {idx}',
    'let ax_id2 = -vds#branch',
    f'wrdata {vgs_file} vdd gate ax_id2 nom_vth0 nom_u0 nom_rdsw nom_nfactor nom_vsat nom_eta0 nom_delta'
    
    
])
    else:
        control_lines.extend([
    f'echo " MONTE CARLO RUN: {idx}"',
    # Dynamically update the specific instance parameters
    f'alterparam vth0_nom = {v_vth0}',
    f'alterparam u0_nom = {v_u0}',
    f'alterparam rdsw_nom = {v_rdsw}',
    f'alterparam nfactor_nom = {v_nfactor}',
    f'alterparam vsat_nom = {v_vsat}',
    f'alterparam eta0_nom = {v_eta0}',
    f'alterparam delta_nom = {v_delta}',
    
    #'dc Vds 0 -1.85 -0.01  Vgs 0 -1.85 -0.185',
    'dc Vds 0 -1.85 -0.01',
    f'let nom_vth0    = {v_vth0} * (v(gate)*0 + 1)',
    f'let nom_u0      = {v_u0} * (v(gate)*0 + 1)',
    f'let nom_rdsw    = {v_rdsw} * (v(gate)*0 + 1)',
    f'let nom_nfactor = {v_nfactor} * (v(gate)*0 + 1)',
    f'let nom_vsat    = {v_vsat} * (v(gate)*0 + 1)',
    f'let nom_eta0    = {v_eta0} * (v(gate)*0 + 1)',
    f'let nom_delta   = {v_delta} * (v(gate)*0 + 1)',
    f'let run_num     = {idx} * (v(gate)*0 + 1)',
    'let ax_id0 = -vds#branch',
    #'set wr_vecnames',
    'set wr_singlescale',
    f'wrdata {vds_file} vdd gate ax_id0 nom_vth0 nom_u0 nom_rdsw nom_nfactor nom_vsat nom_eta0 nom_delta',
    
    #'dc Vgs 0 -1.85 -0.01  Vds -0.01 -0.011 -1',
    #f'let out_vth0    = {v_vth0} * (v(gate)*0 + 1)',
    #f'let out_u0      = {v_u0} * (v(gate)*0 + 1)',
    #f'let out_rdsw    = {v_rdsw} * (v(gate)*0 + 1)',
    #f'let out_nfactor = {v_nfactor} * (v(gate)*0 + 1)',
    #f'let out_vsat    = {v_vsat} * (v(gate)*0 + 1)',
    #f'let out_eta0    = {v_eta0} * (v(gate)*0 + 1)',
    #f'let out_delta   = {v_delta} * (v(gate)*0 + 1)',
    #f'let run_num     = {idx} * (v(gate)*0 + 1)',
    #'let ax_id1 = -vds#branch',
    #f'wrdata {vgs_single_file} vdd gate ax_id1 out_vth0 out_u0 out_rdsw out_nfactor out_vsat out_eta0 nom_delta',
    
    #'dc Vgs 0 -1.85 -0.01  Vds 0 -1.85 -0.37',
    'dc Vgs 0 -1.85 -0.01',
    f'let nom_vth0    = {v_vth0} * (v(gate)*0 + 1)',
    f'let nom_u0      = {v_u0} * (v(gate)*0 + 1)',
    f'let nom_rdsw    = {v_rdsw} * (v(gate)*0 + 1)',
    f'let nom_nfactor = {v_nfactor} * (v(gate)*0 + 1)',
    f'let nom_vsat    = {v_vsat} * (v(gate)*0 + 1)',
    f'let nom_eta0    = {v_eta0} * (v(gate)*0 + 1)',
    f'let nom_delta   = {v_delta} * (v(gate)*0 + 1)',
    f'let run_num     = {idx} * (v(gate)*0 + 1)',
    'let ax_id2 = -vds#branch',
    f'wrdata {vgs_file} vdd gate ax_id2 nom_vth0 nom_u0 nom_rdsw nom_nfactor nom_vsat nom_eta0 nom_delta',
    
    'reset'
])
control_lines.extend(["quit", ".endc", ".end"])

with open("mc_run.spice", "w+") as f:
    # Pre-read the base template so you don't read it from disk over and over
    base_template = open(SPICE_FILE).read()
    print ('opened')


    f.seek(0)    
    f.truncate()  
    f.write(base_template)
    f.write("\n\n")
    f.write("\n".join(control_lines))
      
    f.flush()     


logFile = os.path.join(run_dir, "mc_run.log")
with open(logFile, 'w') as log:
    subprocess.run(["ngspice", "-b","-q", "mc_run.spice"], stdout=log, stderr=subprocess.STDOUT)#, capture_output=True, text=True)

makeCSV(run_dir, N_RUNS)'''
run_dir = '/home/oliviag/ngspice-skywater-sims/montecarlo/mc_output_lhc/nmos_FET_len_0p15_wid_1p6/10000_runs_data_2026-07-09_19-36-16'
getIvVg(N_RUNS, run_dir)
getIvVd(N_RUNS, run_dir)


#end_time = time.perf_counter()
#duration = end_time - start_time
#print(f"Task completed in {duration:.4f} seconds.")
    

    #getIvVd(N_RUNS, output_dir, folder, paramV)

# //////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

