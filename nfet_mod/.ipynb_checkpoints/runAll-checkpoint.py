import os
import subprocess

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

    if current_block:
        out_path = os.path.join(out_dir, f"{prefix}_{current_label}.txt")

        with open(out_path, "w") as out:
            out.writelines(current_block)


def run_splitters(base_dir):

    configs = [
        {
            "file": os.path.join(base_dir, "vg_sweep/p_vgs_sweep_family.txt"),
            "label_col": 5,
            "out_dir": os.path.join(base_dir, "vg_sweep"),
            "prefix": "idVg_vd"
        },
        {
            "file": os.path.join(base_dir, "vd_sweep/p_vds_sweep_family.txt"),
            "label_col": 1,
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

    run_splitters(os.getcwd())

    os.chdir(base_dir)

print("\nDONEEEE")