import numpy as np
import subprocess
import csv
import os
from datetime import datetime
from pathlib import Path
import shutil
import time
#from getCSV import makeCSV
#from getIV import getIvVd
from scipy.stats import qmc


#SPICE_FILE = "paramMC_vds_sweep.spice"
PARENT_DIR = Path("/home/oliviag/ngspice-skywater-sims/montecarlo/mc_output_LHC")
#//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
def getParamOriginal(fet_type, devName, devDir, circuit):
    filePath_s = os.path.join(devDir, "ogparam.txt")
    filePath = Path(filePath_s)
    filePath.touch(exist_ok=True)
    
    #pPath = "mc_output_LHC"
    #ngspice_path = os.path.join("mc_output_lhc", devName)
    #outFile = os.path.join(ngspice_path, "ogparam.txt")
    
    
    pc_control = [f"""* getParam

        .lib "/home/oliviag/skywater130nm/volare/sky130/versions/a918dc7c8e474a99b68c85eb3546b4ed91fe9e7b/sky130A/libs.tech/ngspice/sky130.lib.spice" tt_77k
        {circuit}"""

]
    if fet_type == 0:
    
        p_control = [f"""
            .control
            run
            set filetype=ascii
            
            showmod m.xm1.msky130_fd_pr__nfet_01v8_lvt : vth0 u0 rdsw nfactor vsat eta0 delta > ogparam.txt
            
            
            .endc
            .end"""]
    else:
    
        p_control = [f"""
        .control
        run
        set filetype=ascii
        
        showmod m.xm1.msky130_fd_pr__pfet_01v8_lvt : vth0 u0 rdsw nfactor vsat eta0 delta > ogparam.txt
        
        .endc
        .end"""]
        
    with open("mc_run.spice", "w+") as f:
    # Pre-read the base template so you don't read it from disk over and over
        base_template = pc_control
        #print ('opened')
        f.seek(0)      
        f.truncate()  
        f.write("\n".join(base_template))
        f.write("\n\n")
        f.write("\n".join(p_control))
           
        f.flush()     
    subprocess.run(["ngspice", "-b","-q", "mc_run.spice"])#, capture_output=True, text=True)
    source_file = "ogparam.txt"
    destination_file = os.path.join(dev_dir, "ogparam.txt")
    if os.path.exists(source_file):
        shutil.copy2(source_file, destination_file)
        print(f"done : {devDir}")
    return

    
#//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
def format_spice_params(input_path, output_path):
    """
    Reads the messy ngspice showmod output text, extracts the 7 target 
    parameters, and writes them as a clean, single line of numbers.
    """
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Could not find the spice output at {input_path}")
        
    # 1. Read the raw text file
    with open(input_path, "r") as f:
        content = f.read()
        
    # 2. Break down the text into individual words and numbers
    tokens = content.split()
    
    # The exact 7 parameters you are tracking, in order
    target_params = ["vth0", "u0", "rdsw", "nfactor", "vsat", "eta0", "delta"]
    extracted_values = []
    
    # 3. Match each parameter name with the numeric token immediately following it
    for param in target_params:
        try:
            idx = tokens.index(param)
            val = tokens[idx + 1]
            extracted_values.append(val)
        except (ValueError, IndexError):
            # Fallback default value if ngspice missed a parameter
            extracted_values.append("1.0") 
            
    # 4. Join the numbers with a single space and write to the formatted file
    with open(output_path, "w") as f:
        f.write(" ".join(extracted_values) + "\n")
    return

devices_n = [("nmos_FET_len_0p15_wid_1p6", "XM1 DRAIN GATE 0 0 sky130_fd_pr__nfet_01v8_lvt l=0.15 w=1.6"),
           ("nmos_FET_len_0p19_wid_7", "XM1 DRAIN GATE 0 0 sky130_fd_pr__nfet_01v8_lvt l=0.19 w=7"),
           ("nmos_FET_len_0p25_wid_1p6", "XM1 DRAIN GATE 0 0 sky130_fd_pr__nfet_01v8_lvt l=0.25 w=1.6"),
           ('nmos_FET_len_1_wid_1p6', "XM1 DRAIN GATE 0 0 sky130_fd_pr__nfet_01v8_lvt l=1 w=1.6"),
           ('nmos_FET_len_1_wid_3', "XM1 DRAIN GATE 0 0 sky130_fd_pr__nfet_01v8_lvt l=1 w=3"),
           ('nmos_FET_len_8_wid_1p6', "XM1 DRAIN GATE 0 0 sky130_fd_pr__nfet_01v8_lvt l=8 w=1.6"),
           ('nmos_FET_len_20_wid_0p64', "XM1 DRAIN GATE 0 0 sky130_fd_pr__nfet_01v8_lvt l=20 w=0.64"),
           ('nmos_FET_len_100_wid_100', "XM1 DRAIN GATE 0 0 sky130_fd_pr__nfet_01v8_lvt l=100 w=100")
            ]
           
devices_p = [('pmos_FET_len_8_wid_0p84', "XM1 DRAIN GATE 0 0 sky130_fd_pr__pfet_01v8_lvt l=8 w=0.84"),
           ('pmos_FET_len_0p35_wid_1p6', "XM1 DRAIN GATE 0 0 sky130_fd_pr__pfet_01v8_lvt l=0.35 w=1.6"),
           ('pmos_FET_len_0p5_wid_0p42', "XM1 DRAIN GATE 0 0 sky130_fd_pr__pfet_01v8_lvt l=0.5 w=0.42"),
           ('pmos_FET_len_0p35_wid_0p55', "XM1 DRAIN GATE 0 0 sky130_fd_pr__pfet_01v8_lvt l=0.35 w=0.55"),
           ('pmos_FET_len_0p5_wid_0p64', "XM1 DRAIN GATE 0 0 sky130_fd_pr__pfet_01v8_lvt l=0.5 w=0.64"),
           ('pmos_FET_len_0p35_wid_5', "XM1 DRAIN GATE 0 0 sky130_fd_pr__pfet_01v8_lvt l=0.35 w=0.5"),
           ('pmos_FET_len_2_wid_5', "XM1 DRAIN GATE 0 0 sky130_fd_pr__pfet_01v8_lvt l=2 w=5"),
           ('pmos_FET_len_4_wid_7', "XM1 DRAIN GATE 0 0 sky130_fd_pr__pfet_01v8_lvt l=4 w=7"),
           ('pmos_FET_len_8_wid_1p6', "XM1 DRAIN GATE 0 0 sky130_fd_pr__pfet_01v8_lvt l=8 w=1.6"),
           ('pmos_FET_len_8_wid_5', "XM1 DRAIN GATE 0 0 sky130_fd_pr__pfet_01v8_lvt l=8 w=5")
          ]
           

for dev in devices_n:
    tp = 0
    dev_name = dev[0]
    dev_circ = dev[1]
    
    dev_dir = PARENT_DIR / dev_name
    parameterFile = os.path.join(dev_dir, "ogparam.txt")
    cleaned = os.path.join(dev_dir, "model_parameters.txt")
    format_spice_params(parameterFile, cleaned)
    #dev_dir.mkdir(parents=True, exist_ok=True)

    #getParamOriginal(tp, dev_name, dev_dir, dev_circ)

for dev in devices_p:
    tp = 1
    dev_name = dev[0]
    dev_circ = dev[1]
    
    dev_dir = PARENT_DIR / dev_name
    parameterFile = os.path.join(dev_dir, "ogparam.txt")
    cleaned = os.path.join(dev_dir, "model_parameters.txt")
    format_spice_params(parameterFile, cleaned)
    #dev_dir.mkdir(parents=True, exist_ok=True)
    #getParamOriginal(tp, dev_name, dev_dir, dev_circ)