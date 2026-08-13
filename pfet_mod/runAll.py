import os
import subprocess
from pfet_lib import buildNetlist

# =========================
# GEOMETRIES
# =========================
directories = [
    #"l_0p35_w_1p6",
    #"l_0p50_w_0p42",
    #"l_2p0_w_5p0",
    #"l_8p0_w_0p84",
    #"l_8p0_w_5p0",
    #"l_0p35_w_0p55",
    #"l_0p35_w_5p0",
    #"l_0p50_w_0p64",
    #"l_4p0_w_7p0",
    #"l_8p0_w_1p6"
]
circuit_lib = [ 
    #"XM1 VDD gate GND GND sky130_fd_pr__pfet_01v8_lvt l=0.35 w=1.6 mult=1 m=1",
    #"XM1 VDD gate GND GND sky130_fd_pr__pfet_01v8_lvt l=0.5 w=0.42 mult=1 m=1",
    #"XM1 VDD gate GND GND sky130_fd_pr__pfet_01v8_lvt l=2 w=5 mult=1 m=1",
    #"XM1 VDD gate GND GND sky130_fd_pr__pfet_01v8_lvt l=8 w=0.84 mult=3 m=3",
    #"XM1 VDD gate GND GND sky130_fd_pr__pfet_01v8_lvt l=8 w=5 mult=3 m=3",
    #"XM1 VDD gate GND GND sky130_fd_pr__pfet_01v8_lvt l=0.35 w=0.55 mult=1 m=1",
    #"XM1 VDD gate GND GND sky130_fd_pr__pfet_01v8_lvt l=0.35 w=5 mult=3 m=3",
    #"XM1 VDD gate GND GND sky130_fd_pr__pfet_01v8_lvt l=0.5 w=0.64 mult=2 m=2",
    #"XM1 VDD gate GND GND sky130_fd_pr__pfet_01v8_lvt l=4 w=7 mult=3 m=3",
    #"XM1 VDD gate GND GND sky130_fd_pr__pfet_01v8_lvt l=8 w=1.6 mult=3 m=3"
    ]

# =========================
# SPLITTER CONFIG
# =========================
def format_val(x):
    x = abs(float(x))
    return f"{x:.3f}".replace(".", "p")


def process_file(file_path, label_col, out_dir, prefix):

    os.makedirs(out_dir, exist_ok=True)

    with open(file_path, "r") as f:
        lines = f.readlines()

    current_block = []
    current_label = None


    for line in lines:

        if not line.strip():
            continue

        cols = line.split()
        if len(cols) <= label_col:
            continue

        label = format_val(cols[label_col])

        if current_label is None:
            current_label = label

        if label != current_label:

            out_path = os.path.join(out_dir, f"{prefix}_{current_label}.txt")

            with open(out_path, "w") as out:
                out.writelines(current_block)

            current_block = []
            current_label = label

        current_block.append(line)
    if current_label == '0p010' or current_label == '0p370' or current_label == '0p740' or current_label == '1p110' or current_label == '1p480' or current_label == '1p850':
        if current_block:
            out_path = os.path.join(out_dir, f"{prefix}_{current_label}.txt")
    
            with open(out_path, "w") as out:
                out.writelines(current_block)


def run_splitters(base_dir):

    configs = [
        {
            "file": os.path.join(base_dir, "vg_sweep/p_vgs_sweep_family.txt"),
            "label_col": 1,
            "out_dir": os.path.join(base_dir, "vg_sweep"),
            "prefix": "idVg_vd"
        },
        {
            "file": os.path.join(base_dir, "vd_sweep/p_vds_sweep_family.txt"),
            "label_col": 2,
            "out_dir": os.path.join(base_dir, "vd_sweep"),
            "prefix": "idVd_vg"
        }
    ]

    for cfg in configs:
        if os.path.isfile(cfg["file"]):
            process_file(cfg["file"], cfg["label_col"], cfg["out_dir"], cfg["prefix"])
        else:
            print(f"Missing file: {cfg['file']}")


# =========================
# MAIN PIPELINE
# =========================
base_dir = os.getcwd()
for dev, circ in zip(directories, circuit_lib):
    folder_path = os.path.join(base_dir, dev)
    os.chdir(folder_path)
    print(f"RUNNING: {dev}")
    buildNetlist(circ, dev)
    #dev_dir = os.path.join(base_dir, dev)
    run_splitters(os.getcwd())
    os.chdir(base_dir)
print("Finished Simulating")
    
    

'''base_dir = os.getcwd()

for folder in directories:

    folder_path = os.path.join(base_dir, folder)

    if not os.path.isdir(folder_path):
        print(f"Missing dir: {folder}")
        continue

    #print("\n" + "="*60)
    #print(f"RUNNING: {folder}")
    #print("="*60)

    os.chdir(folder_path)

    spice_files = ["sweeps.spice"]

    for spice_file in spice_files:

        if not os.path.isfile(spice_file):
            print(f"Missing spice file: {spice_file}")
            continue

        log_file = spice_file.replace(".spice", ".log")

        print(f"Running ngspice: {spice_file}")

        with open(log_file, "w") as log:
            subprocess.run(
                ["ngspice", "-b", spice_file],
                stdout=log,
                stderr=subprocess.STDOUT
            )

    # AFTER simulation → run splitter
    run_splitters(os.getcwd())

    os.chdir(base_dir)

print("\nDONEEEE")'''