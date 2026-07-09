import csv
import numpy as np
import os
import sys
def makeCSV(path, runs):
    inde = np.arange(runs)
    
    for i in inde:
    # Define your file paths
        #input_file = f"/home/oliviag/ngspice-skywater-sims/sim_data_vd/{i}_mosfetvgs_mc_all.dat"
        #output_file = f"/home/oliviag/ngspice-skywater-sims/sim_data_vd/{i}_mosfetVGS_MC_all.csv"
        input_file = f"{path}/output{i}.dat"
        output_file = f"{path}/output{i}.csv"
        
        if not os.path.exists(input_file):
            continue
        # Your exact custom headers (including the initial sweep scale column)
        headers = ["vSweep", "run_num", "vd", "id", "vth0", "u0", "rdsw", "nfactor", "vsat", "eta0"]
        
        with open(input_file, 'r') as infile, open(output_file, 'w', newline='') as outfile:
            writer = csv.writer(outfile)
            
            # 1. Write the clean header first
            writer.writerow(headers)
            
            # 2. Skip NGSPICE's internal header line, then process the rows
            next(infile) 
            for line in infile:
                # Split the line by any whitespace and filter out empty strings
                row = [val for val in line.strip().split() if val]
                if row:
                    writer.writerow(row)
    '''inde2 = ['0','1','2','3','4']
    for i in inde2:
    # Define your file paths
        input_file = f"/home/oliviag/ngspice-skywater-sims/sim_data_vd/{i}_mosfetvds_mc_all.dat"
        output_file = f"/home/oliviag/ngspice-skywater-sims/sim_data_vd/{i}_mosfetVDS_MC_all.csv"
        
        # Your exact custom headers (including the initial sweep scale column)
        headers = ["vSweep", "run_num", "vd", "id", "vth0", "u0", "rdsw", "nfactor", "vsat", "eta0"]
        
        with open(input_file, 'r') as infile, open(output_file, 'w', newline='') as outfile:
            writer = csv.writer(outfile)
            
            # 1. Write the clean header first
            writer.writerow(headers)
            
            # 2. Skip NGSPICE's internal header line, then process the rows
            next(infile) 
            for line in infile:
                # Split the line by any whitespace and filter out empty strings
                row = [val for val in line.strip().split() if val]
                if row:
                    writer.writerow(row)'''
    return