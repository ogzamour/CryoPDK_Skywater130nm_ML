import os
import subprocess
from nfet_lib import buildNetlist 

# =========================
# GEOMETRIES
# =========================
directories = [
    "l_0p15_w_1p6",
    "l_0p19_w_7p0",
    "l_0p25_w_1p6",
    "l_1p0_w_1p6",
    "l_1p0_w_3p0",
    "l_8p0_w_1p6",
    "l_20p0_w_0p64",
    "l_100p0_w_100p0"
]
circuit_lib = [
    "XM1 VDD GATE GND GND sky130_fd_pr__nfet_01v8_lvt l=0.15 w=1.6 mult=1 m=1",
    "XM1 VDD GATE GND GND sky130_fd_pr__nfet_01v8_lvt l=0.19 w=7 mult=1 m=1",
    "XM1 VDD GATE GND GND sky130_fd_pr__nfet_01v8_lvt l=0.25 w=1.6 mult=1 m=1",
    "XM1 VDD GATE GND GND sky130_fd_pr__nfet_01v8_lvt l=1 w=1.6 mult=1 m=1",
    "XM1 VDD GATE GND GND sky130_fd_pr__nfet_01v8_lvt l=1 w=3 mult=1 m=1",
    "XM1 VDD GATE GND GND sky130_fd_pr__nfet_01v8_lvt l=8 w=1.6 mult=1 m=1",
    "XM1 VDD GATE GND GND sky130_fd_pr__nfet_01v8_lvt l=20 w=0.64 mult=1 m=1",
    "XM1 VDD GATE GND GND sky130_fd_pr__nfet_01v8_lvt l=100 w=100 mult=1 m=1"
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