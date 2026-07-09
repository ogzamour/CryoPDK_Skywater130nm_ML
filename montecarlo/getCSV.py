import csv
import numpy as np
import os
import sys

'''def getConf(base_dir):
    configs = [
        
            #"file": os.path.join(base_dir, "vgs_sweep.dat"),
            "label_col": 2,
            "out_dir": base_dir,
            "prefix": "idVg_vd",
            "headers": "sweep_var,vdd,gate,ax_id,out_vth0,out_u0,out_rdsw,out_nfactor,out_vsat,out_eta0"

        
    ]

    return config'''
#//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
def format_val(x):
    """Converts float values to a safe filename string (e.g., 0.185 -> 0p185)"""
    try:
        x = abs(float(x))
        return f"{x:.3f}".replace(".", "p")
    except ValueError:
        return str(x).strip()

#"vgs_sweep_0p01_vd.dat"
#//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
def process_and_split_to_csv(base_dir, n):
    cfg = getConf(base_dir)
    split_col = cfg["label_col"]
    prefix = cfg["prefix"]
    headers = cfg["headers"].strip() + "\n"

    #print(f"\nScanning for files in: {directory}")
    #print(f"Splitting on Column Index: {split_col}")
    #print("----------------------------------------")

    total_csv_written = 0

    for i in range(runs):
        input_file1 = os.path.join(base_dir, "vgs_sweep.dat")
        input_file2 = os.path.join(base_dir, "vds_sweep.dat")
        input_file3 = os.path.join(base_dir, "vgs_sweep_0p01_vd.dat")
       
        
        
        with open(input_file1, "r") as f:
            lines = f.readlines()

        current_block_rows = []
        current_val_string = None
        
        for line in lines:
            cleaned_line = line.strip()
            if not cleaned_line:
                continue
                
            # Skip Ngspice text headers if wr_vecnames was active
            if cleaned_line.startswith(("title", "date", "plot", "v", "i", "a", "o", "r")):
                continue
                
            cols = cleaned_line.split()
            if len(cols) <= split_col:
                continue
                
            # Track the value of the target split column
            raw_val = cols[split_col]
            val_string = format_val(raw_val)
            
            # Initialize anchor value on the first valid line
            if current_val_string is None:
                current_val_string = val_string
                
            # Boundary Change Detected -> Dump accumulated block directly to a CSV
            if val_string != current_val_string:
                out_filename = f"{prefix}_file{i}_val_{current_val_string}.csv"
                out_path = os.path.join(directory, out_filename)
                
                with open(out_path, "w") as outf:
                    outf.write(headers)
                    outf.writelines(current_block_rows)
                    
                total_csv_written += 1
                current_block_rows = []
                current_val_string = val_string
            
            # Convert space-delimited raw row directly to comma-separated format
            csv_row = ",".join(cols) + "\n"
            current_block_rows.append(csv_row)
            
        # Write out final remaining block for this file
        if current_block_rows:
            out_filename = f"{prefix}_file{i}_val_{current_val_string}.csv"
            out_path = os.path.join(directory, out_filename)
            
            with open(out_path, "w") as outf:
                outf.write(headers)
                outf.writelines(current_block_rows)
                
            total_csv_written += 1

    #print(f"----------------------------------------")
    #print(f"Done. Successfully generated {total_csv_written} CSV files.")
#//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

def makeCSV(runPath, simNum):
    index = list(range(simNum))
    for i in index:
    
        #input_file = f"/home/oliviag/ngspice-skywater-sims/sim_data_vd/{i}_mosfetvgs_mc_all.dat"
        #output_file = f"/home/oliviag/ngspice-skywater-sims/sim_data_vd/{i}_mosfetVGS_MC_all.csv"
        input_vg = f"{runPath}/run_{i}/vgs_sweep.dat"
        output_vg = f"{runPath}/run_{i}/vgs_sweep.csv"

        input_vd = f"{runPath}/run_{i}/vds_sweep.dat"
        output_vd = f"{runPath}/run_{i}/vds_sweep.csv"
        

        
        headers = ["vSweep", "vd", "vg", "id", "vth0_nom", "u0_nom", "rdsw_nom", "nfactor_nom", "vsat_nom", "eta0_nom", "delta_nom"]
        
        with open(input_vg, 'r') as infile, open(output_vg, 'w', newline='') as outfile:
            writer = csv.writer(outfile)
            
       
            writer.writerow(headers)
            
           
            next(infile) 
            for line in infile:
               
                row = [val for val in line.strip().split() if val]
                if row:
                    writer.writerow(row)
        with open(input_vd, 'r') as infile, open(output_vd, 'w', newline='') as outfile:
            writer = csv.writer(outfile)
            
       
            writer.writerow(headers)
            
           
            next(infile) 
            for line in infile:
               
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