import numpy as np
import matplotlib as plt
import subprocess
import csv
import os
from datetime import datetime
from pathlib import Path
import time
#from getCSV import makeCSV
#from getIV import getIvVd
from scipy.stats import qmc
N_RUNS = 3
#SPICE_FILE = "nfet_base.spice"
PARENT_DIR = Path.home() / "ngspice-skywater-sims/montecarlo/mc_output_lhc"
#//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
device_library = [("nmos_FET_len_0p15_wid_1p6", "XM1 DRAIN GATE 0 0 sky130_fd_pr__nfet_01v8_lvt l=0.15 w=1.6 mult=1 m=1",'n'),
           ("nmos_FET_len_0p19_wid_7", "XM1 DRAIN GATE 0 0 sky130_fd_pr__nfet_01v8_lvt l=0.19 w=7 mult=1 m=1","n"),
           ("nmos_FET_len_0p25_wid_1p6", "XM1 DRAIN GATE 0 0 sky130_fd_pr__nfet_01v8_lvt l=0.25 w=1.6 mult=1 m=1",'n'),
           ('nmos_FET_len_1_wid_1p6', "XM1 DRAIN GATE 0 0 sky130_fd_pr__nfet_01v8_lvt l=1 w=1.6 mult=1 m=1",'n'),
           ('nmos_FET_len_1_wid_3', "XM1 DRAIN GATE 0 0 sky130_fd_pr__nfet_01v8_lvt l=1 w=3 mult=1 m=1",'n'),
           ('nmos_FET_len_8_wid_1p6', "XM1 DRAIN GATE 0 0 sky130_fd_pr__nfet_01v8_lvt l=8 w=1.6 mult=1 m=1",'n'),
           ('nmos_FET_len_20_wid_0p64', "XM1 DRAIN GATE 0 0 sky130_fd_pr__nfet_01v8_lvt l=20 w=0.64 mult=1 m=1",'n'),
           ('nmos_FET_len_100_wid_100', "XM1 DRAIN GATE 0 0 sky130_fd_pr__nfet_01v8_lvt l=100 w=100 mult=1 m=1",'n'),
           ('pmos_FET_len_8_wid_0p84', "XM1 DRAIN GATE 0 0 sky130_fd_pr__pfet_01v8_lvt l=8 w=0.84 mult=3 m=3",'p'),
           ('pmos_FET_len_0p35_wid_1p6', "XM1 DRAIN GATE 0 0 sky130_fd_pr__pfet_01v8_lvt l=0.35 w=1.6 mult=1 m=1",'p'),
           ('pmos_FET_len_0p5_wid_0p42', "XM1 DRAIN GATE 0 0 sky130_fd_pr__pfet_01v8_lvt l=0.5 w=0.42 mult=1 m=1",'p'),
           ('pmos_FET_len_0p35_wid_0p55', "XM1 DRAIN GATE 0 0 sky130_fd_pr__pfet_01v8_lvt l=0.35 w=0.55 mult=1 m=1",'p'),
           ('pmos_FET_len_0p5_wid_0p64', "XM1 DRAIN GATE 0 0 sky130_fd_pr__pfet_01v8_lvt l=0.5 w=0.64 mult=2 m=2",'p'),
           ('pmos_FET_len_0p35_wid_5', "XM1 DRAIN GATE 0 0 sky130_fd_pr__pfet_01v8_lvt l=0.35 w=0.5 mult=3 m=3",'p'),
           ('pmos_FET_len_2_wid_5', "XM1 DRAIN GATE 0 0 sky130_fd_pr__pfet_01v8_lvt l=2 w=5 mult=1 m=1",'p'),
           ('pmos_FET_len_4_wid_7', "XM1 DRAIN GATE 0 0 sky130_fd_pr__pfet_01v8_lvt l=4 w=7 mult=3 m=3",'p'),
           ('pmos_FET_len_8_wid_1p6', "XM1 DRAIN GATE 0 0 sky130_fd_pr__pfet_01v8_lvt l=8 w=1.6 mult=3 m=3",'p'),
           ('pmos_FET_len_8_wid_5', "XM1 DRAIN GATE 0 0 sky130_fd_pr__pfet_01v8_lvt l=8 w=5 mult=3 m=3",'p')
]

#//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
def getHypercube(num_samples, runDir):
    num_vars = 7 # e.g., Width (W) and Length (L)
    p = np.loadtxt(os.path.join(dev_dir, "model_parameters.txt")) #original parameters for setting bounds
    
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
def deviceTemplate(dev_dir, dev_param):
    home = str(Path.home())
    #nfet_meas = 
    
    device_cmd = f"""* NMOS sweep (Sky130) 


{dev_param} nf=1 ad='floor((nf+1)/2) * w/nf * 0.29' as='floor((nf+2)/2) * w/nf * 0.29' pd='2 * floor((nf+1)/2) * (w/nf + 0.29)' ps='2 * floor((nf+2)/2) * (w/nf + 0.29)' nrd='0.29 / w' nrs='0.29 / w' sa=0 sb=0 sd=0 
.lib "{home}/skywater130nm/volare/sky130/versions/a918dc7c8e474a99b68c85eb3546b4ed91fe9e7b/sky130A/libs.tech/ngspice/sky130.lib.spice" tt_77k

Vgs gate GND 0
Vds VDD GND 1.48
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
start_time = time.perf_counter()
folder = datetime.now().strftime("data_%Y-%m-%d_%H-%M-%S")
for device in device_library:
    deviceName = device[0]
    circuit = device[1]
    fet = device[2]
    dev_dir = PARENT_DIR / deviceName
    run_dir = dev_dir / folder
    run_dir.mkdir(parents=True, exist_ok=True)
    SPICE_FILE = os.path.join(dev_dir, "mc_template.spice") 
        
     
    vth0_c = 1
    u0_c = 1
    rdsw_c = 1
    nfactor_c = 1
    vsat_c = 1
    eta0_c = 1
    delta_c = 1
    
    getHypercube(N_RUNS, run_dir)
    
    lhs_runs = np.loadtxt(os.path.join(run_dir, "lhs_parameters.txt"))
    #vth0_v, u0_v, rdsw_v, nfactor_v, vsat_v, eta0_v, delta_v = lhs_runs.T
    
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
        vds_file = outPath / "vds_sweep.csv"
        vgs_single_file = outPath / "vgs_sweep_0p01_vd.csv"
        vgs_file = outPath / "vgs_sweep.csv"
    
        if fet == 'n':
            control_lines.extend([
        f'echo " MONTE CARLO RUN: {idx}"',
        # Dynamically update the specific instance parameters
        f'altermod @m.xm1.msky130_fd_pr__nfet_01v8_lvt[vth0]    = {v_vth0}',
        f'altermod @m.xm1.msky130_fd_pr__nfet_01v8_lvt[u0]      = {v_u0}',
        f'altermod @m.xm1.msky130_fd_pr__nfet_01v8_lvt[rdsw]    = {v_rdsw}',
        f'altermod @m.xm1.msky130_fd_pr__nfet_01v8_lvt[nfactor] = {v_nfactor}',
        f'altermod @m.xm1.msky130_fd_pr__nfet_01v8_lvt[vsat]    = {v_vsat}',
        f'altermod @m.xm1.msky130_fd_pr__nfet_01v8_lvt[eta0]    = {v_eta0}',
        f'altermod @m.xm1.msky130_fd_pr__nfet_01v8_lvt[delta]   = {v_delta}',
        
        'dc Vds 0 1.85 0.01 Vgs 0 1.85 0.185',
        f'let out_vth0    = {v_vth0} * (v(gate)*0 + 1)',
        f'let out_u0      = {v_u0} * (v(gate)*0 + 1)',
        f'let out_rdsw    = {v_rdsw} * (v(gate)*0 + 1)',
        f'let out_nfactor = {v_nfactor} * (v(gate)*0 + 1)',
        f'let out_vsat    = {v_vsat} * (v(gate)*0 + 1)',
        f'let out_eta0    = {v_eta0} * (v(gate)*0 + 1)',
        f'let out_delta   = {v_delta} * (v(gate)*0 + 1)',
        f'let run_num     = {idx} * (v(gate)*0 + 1)',
        'let ax_id0 = -vds#branch',
        'set wr_vecnames',
        'set wr_singlescale',
        f'wrdata {vds_file} vdd gate ax_id0 out_vth0 out_u0 out_rdsw out_nfactor out_vsat out_eta0',
        
        'dc Vgs 0 1.85 0.01 Vds 0.01 0.01 1',
        f'let out_vth0    = {v_vth0} * (v(gate)*0 + 1)',
        f'let out_u0      = {v_u0} * (v(gate)*0 + 1)',
        f'let out_rdsw    = {v_rdsw} * (v(gate)*0 + 1)',
        f'let out_nfactor = {v_nfactor} * (v(gate)*0 + 1)',
        f'let out_vsat    = {v_vsat} * (v(gate)*0 + 1)',
        f'let out_eta0    = {v_eta0} * (v(gate)*0 + 1)',
        f'let out_delta   = {v_delta} * (v(gate)*0 + 1)',
        f'let run_num     = {idx} * (v(gate)*0 + 1)',
        'let ax_id1 = -vds#branch',
        f'wrdata {vgs_single_file} vdd gate ax_id1 out_vth0 out_u0 out_rdsw out_nfactor out_vsat out_eta0',
        
        'dc Vgs 0 1.85 0.01 Vds 0 1.85 0.185',
        f'let out_vth0    = {v_vth0} * (v(gate)*0 + 1)',
        f'let out_u0      = {v_u0} * (v(gate)*0 + 1)',
        f'let out_rdsw    = {v_rdsw} * (v(gate)*0 + 1)',
        f'let out_nfactor = {v_nfactor} * (v(gate)*0 + 1)',
        f'let out_vsat    = {v_vsat} * (v(gate)*0 + 1)',
        f'let out_eta0    = {v_eta0} * (v(gate)*0 + 1)',
        f'let out_delta   = {v_delta} * (v(gate)*0 + 1)',
        f'let run_num     = {idx} * (v(gate)*0 + 1)',
        'let ax_id2 = -vds#branch',
        f'wrdata {vgs_file} vdd gate ax_id2 out_vth0 out_u0 out_rdsw out_nfactor out_vsat out_eta0',
        
        
        'reset'
    ])
        else:
            control_lines.extend([
        f'echo " MONTE CARLO RUN: {idx}"',
        # Dynamically update the specific instance parameters
        f'altermod @m.xm1.msky130_fd_pr__pfet_01v8_lvt[vth0]    = {v_vth0}',
        f'altermod @m.xm1.msky130_fd_pr__pfet_01v8_lvt[u0]      = {v_u0}',
        f'altermod @m.xm1.msky130_fd_pr__pfet_01v8_lvt[rdsw]    = {v_rdsw}',
        f'altermod @m.xm1.msky130_fd_pr__pfet_01v8_lvt[nfactor] = {v_nfactor}',
        f'altermod @m.xm1.msky130_fd_pr__pfet_01v8_lvt[vsat]    = {v_vsat}',
        f'altermod @m.xm1.msky130_fd_pr__pfet_01v8_lvt[eta0]    = {v_eta0}',
        f'altermod @m.xm1.msky130_fd_pr__pfet_01v8_lvt[delta]   = {v_delta}',
        
        'dc Vds 0 -1.85 -0.01  Vgs 0 -1.85 -0.185',
        f'let out_vth0    = {v_vth0} * (v(gate)*0 + 1)',
        f'let out_u0      = {v_u0} * (v(gate)*0 + 1)',
        f'let out_rdsw    = {v_rdsw} * (v(gate)*0 + 1)',
        f'let out_nfactor = {v_nfactor} * (v(gate)*0 + 1)',
        f'let out_vsat    = {v_vsat} * (v(gate)*0 + 1)',
        f'let out_eta0    = {v_eta0} * (v(gate)*0 + 1)',
        f'let out_delta   = {v_delta} * (v(gate)*0 + 1)',
        f'let run_num     = {idx} * (v(gate)*0 + 1)',
        'let ax_id0 = -vds#branch',
        'set wr_vecnames',
        'set wr_singlescale',
        f'wrdata {vds_file} vdd gate ax_id0 out_vth0 out_u0 out_rdsw out_nfactor out_vsat out_eta0',
        
        'dc Vgs 0 -1.85 -0.01  Vds -0.01 -0.011 -1',
        f'let out_vth0    = {v_vth0} * (v(gate)*0 + 1)',
        f'let out_u0      = {v_u0} * (v(gate)*0 + 1)',
        f'let out_rdsw    = {v_rdsw} * (v(gate)*0 + 1)',
        f'let out_nfactor = {v_nfactor} * (v(gate)*0 + 1)',
        f'let out_vsat    = {v_vsat} * (v(gate)*0 + 1)',
        f'let out_eta0    = {v_eta0} * (v(gate)*0 + 1)',
        f'let out_delta   = {v_delta} * (v(gate)*0 + 1)',
        f'let run_num     = {idx} * (v(gate)*0 + 1)',
        'let ax_id1 = -vds#branch',
        f'wrdata {vgs_single_file} vdd gate ax_id1 out_vth0 out_u0 out_rdsw out_nfactor out_vsat out_eta0',
        
        'dc Vgs 0 -1.85 -0.01  Vds 0 -1.85 -0.37',
        f'let out_vth0    = {v_vth0} * (v(gate)*0 + 1)',
        f'let out_u0      = {v_u0} * (v(gate)*0 + 1)',
        f'let out_rdsw    = {v_rdsw} * (v(gate)*0 + 1)',
        f'let out_nfactor = {v_nfactor} * (v(gate)*0 + 1)',
        f'let out_vsat    = {v_vsat} * (v(gate)*0 + 1)',
        f'let out_eta0    = {v_eta0} * (v(gate)*0 + 1)',
        f'let out_delta   = {v_delta} * (v(gate)*0 + 1)',
        f'let run_num     = {idx} * (v(gate)*0 + 1)',
        'let ax_id2 = -vds#branch',
        f'wrdata {vgs_file} vdd gate ax_id2 out_vth0 out_u0 out_rdsw out_nfactor out_vsat out_eta0',
        
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
    
end_time = time.perf_counter()
duration = end_time - start_time
print(f"Task completed in {duration:.4f} seconds.")
    
    #makeCSV(output_dir, N_RUNS)
    #getIvVd(N_RUNS, output_dir, folder, paramV)
    
    
#//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
    
