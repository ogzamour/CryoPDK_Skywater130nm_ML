import numpy as np
import subprocess
import csv
import os
from datetime import datetime
from pathlib import Path
import time
from getCSV import makeCSV
from getIV import getIvVd
from scipy.stats import qmc

N_RUNS = 5
SPICE_FILE = "nfet_base.spice"
PARENT_DIR = Path("/home/oliviag/ngspice-skywater-sims/montecarlo/mc_output_LHC")
deviceName = "nmos_FET_len_0p15_wid_1p6"
dev_dir = PARENT_DIR / deviceName
#dev_dir.mkdir(parents=True, exist_ok=True)

folder = datetime.now().strftime("data_%Y-%m-%d_%H-%M-%S")
run_dir = dev_dir / folder
run_dir.mkdir(parents=True, exist_ok=True)


#//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
def getHypercube(num_samples, runDir):
    num_vars = 7 # e.g., Width (W) and Length (L)
    p = np.loadtxt(os.path.join(dev_dir, "model_parameters")) #original parameters for setting bounds
    
    sampler = qmc.LatinHypercube(d=num_vars)
    sample_matrix = sampler.random(n=num_samples)

    floor = 0.9 * p
    ceiling = 1.1 * p

    scaled_matrix = qmc.scale(sample_matrix, floor, ceiling)
    
    # Export to a text file for ngspice to read
    np.savetxt(os.path.join(runDir,'lhs_parameters.txt'), scaled_matrix, fmt='%.16e')
    return

#//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

#vg_bias_folders = ["Vg_0p01", "Vg_0p37", "Vg_0p74", "Vg_1p11", "Vg_1p48", "Vg_1p85"]
#vd_bias_volders = ["Vd_0p01", "Vd_0p37", "Vd_0p74", "Vd_1p11", "Vd_1p48", "Vd_1p85"]

vth0_c = 1
u0_c = 1
rdsw_c = 1
nfactor_c = 1
vsat_c = 1
eta0_c = 1
delta_c = 1

'''paramV = []

if vth0: paramV.append("vth0")
if u0: paramV.append("u0")
if rdsw: paramV.append("rdsw")
if nfactor: paramV.append("nfactor")
if vsat: paramV.append("vsat")
if eta0: paramV.append("eta0")
if delta: paramV.append("delta")'''

getHypercube(N_RUNS, run_dir)

lhs_runs = np.loadtxt(os.path.join(run_dir, "lhs_parameters.txt"))
vth0_v, u0_v, rdsw_v, nfactor_v, vsat_v, eta0_v, delta_v = lhs_runs.T


start_time = time.perf_counter()



cmd = [f"""
        .control
        set noaskquit
        run
        
        
        set outDir = {run_dir}
        let i_max = {N_RUNS}
        let idx = 0
        let i1 = 1
        """]

#cmd.append('dowhile (idx < i_max)')

cmd.append("""   
    *echo "========================================="
    echo " MONTE CARLO RUN: $&idx" 
    *echo "========================================="
    let vth0_arr = [ { " ".join(map(str, vth0_v)) } ]
    let u0_arr   = [ { " ".join(map(str, u0_v)) } ]
    let rdsw_arr = [ { " ".join(map(str, rdsw_v)) } ]
    let nfac_arr = [ { " ".join(map(str, nfactor_v)) } ]
    let vsat_arr = [ { " ".join(map(str, vsat_v)) } ]
    let eta0_arr = [ { " ".join(map(str, eta0_v)) } ]
    let delt_arr = [ { " ".join(map(str, delta_v)) } ]
    """)

nfet_loop = ("""
    
    dowhile (idx < i_max)
        echo " MONTE CARLO RUN: $&idx"
        *showmod m.xm1.msky130_fd_pr__nfet_01v8_lvt : vth0 u0 rdsw nfactor vsat eta0 delta 
        altermod @m.xm1.msky130_fd_pr__nfet_01v8_lvt[vth0]    = vth0_arr[idx]
        altermod @m.xm1.msky130_fd_pr__nfet_01v8_lvt[u0]      = u0_arr[idx]
        altermod @m.xm1.msky130_fd_pr__nfet_01v8_lvt[rdsw]    = rdsw_arr[idx]
        altermod @m.xm1.msky130_fd_pr__nfet_01v8_lvt[nfactor] = nfac_arr[idx]
        altermod @m.xm1.msky130_fd_pr__nfet_01v8_lvt[vsat]    = vsat_arr[idx]
        altermod @m.xm1.msky130_fd_pr__nfet_01v8_lvt[eta0]    = eta0_arr[idx]
        altermod @m.xm1.msky130_fd_pr__nfet_01v8_lvt[delta]   = delt_arr[idx]

        
        
        dc Vds 0 1.85 0.01  Vgs 0 1.85 0.185
        setplot
        display
        shell pwd
        set curplottype=family
        let ax_id0 = -vds#branch
        set wr_vecnames
        set wr_singlescale
        set raw_file = "$outDir/run_{$&idx}/vds_sweep.dat"
        wrdata $raw_file vdd gate ax_id0 out_vth0 out_u0 out_rdsw out_nfactor out_vsat out_eta0
        
        destroy dc1
        dc Vgs 0 1.85 0.01  Vds 0.01 0.01 1
        setplot
        display
        shell pwd
        set curplottype=family
        let ax_id1 = -vds#branch
        set wr_vecnames
        set wr_singlescale
        set raw_file = "$outDir/run_{$&idx}/vgs_sweep_0p01_vd.dat"
        wrdata $raw_file vdd gate ax_id1 out_vth0 out_u0 out_rdsw out_nfactor out_vsat out_eta0

        destroy dc2
        dc Vgs 0 1.85 0.01  Vds 0 1.85 0.185
        setplot
        display
        shell pwd
        set curplottype=family
        let ax_id2 = -vds#branch
        set wr_vecnames
        set wr_singlescale
        set raw_file = "$outDir/run_{$&idx}/vgs_sweep.dat"
        wrdata $raw_file vdd gate ax_id2 out_vth0 out_u0 out_rdsw out_nfactor out_vsat out_eta0
        
        let idx = idx + i1
    
  end


quit
.endc

.end
""")
cmd.append(nfet_loop)

with open("mc_run.spice", "w+") as f:
    # Pre-read the base template so you don't read it from disk over and over
    base_template = open(SPICE_FILE).read()
    print ('opened')


    f.seek(0)      # Move the "cursor" back to the very top of the file
        #print('fseek')
    f.truncate()  # Delete everything currently in the file
        #print('truncate')
        # Write the fresh data
    f.write(base_template)
    f.write("\n\n")
    f.write("\n".join(cmd))
       # print('written')
    f.flush()     # Force Python to actually write the data to the hard drive immediately
       # print('flush')
        # Run ngspice safely
subprocess.run(["ngspice", "-b","-q", "mc_run.spice"])#, capture_output=True, text=True)

end_time = time.perf_counter()
duration = end_time - start_time

print(f"Task completed in {duration:.4f} seconds.")

#makeCSV(output_dir, N_RUNS)
#getIvVd(N_RUNS, output_dir, folder, paramV)



'''let out_vth0    = v_vth0*(v(drain)*0 + 1)
        let out_u0      = v_u0 * (v(DRAIN)*0 + 1)
        let out_rdsw    = v_rdsw * (v(DRAIN)*0 + 1)
        let out_nfactor = v_nfactor * (v(DRAIN)*0 + 1)
        let out_vsat    = v_vsat * (v(DRAIN)*0 + 1)
        let out_eta0    = v_eta0 * (v(DRAIN)*0 + 1)
        let out_delta   = v_delta * (v(DRAIN)*0 + 1)
        let run_num     = $&idx * (v(DRAIN)*0 + 1)'''