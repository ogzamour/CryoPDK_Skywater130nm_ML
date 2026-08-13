import os

# =========================
# CONFIGS
# =========================
configs = [
    {
        "file": "vg_sweep/p_vgs_sweep_family.txt",
        "label_col": 5,
        "out_dir": "vg_sweep",
        "prefix": "idVg_vd"
    },
    {
        "file": "vd_sweep/p_vds_sweep_family.txt",
        "label_col": 1,
        "out_dir": "vd_sweep",
        "prefix": "idVd_vg"
    }
]
# =========================


def format_val(x):
    x = abs(float(x))
    return f"{x:.3f}".replace(".", "p")


def get_col(line, col):
    return line.split()[col]


def process(cfg):

    file_path = cfg["file"]
    col = cfg["label_col"]
    out_dir = cfg["out_dir"]
    prefix = cfg["prefix"]

    os.makedirs(out_dir, exist_ok=True)

    with open(file_path, "r") as f:
        lines = f.readlines()

    print(f"\nProcessing: {file_path}")
    print(f"Label col: {col}")
    print("----------------------------------------")

    current_block = []
    current_label = None
    file_count = 0

    for line in lines:

        if not line.strip():
            continue

        cols = line.split()
        if len(cols) <= col:
            continue

        label = format_val(cols[col])

        # first line
        if current_label is None:
            current_label = label

        # boundary detected → write previous block
        if label != current_label:

            out_path = os.path.join(
                out_dir,
                f"{prefix}_{current_label}.txt"
            )

            with open(out_path, "w") as out:
                out.writelines(current_block)

            print(f"Wrote {out_path} ({len(current_block)} lines)")
            file_count += 1

            current_block = []
            current_label = label

        current_block.append(line)

    # write final block
    if current_block:
        out_path = os.path.join(
            out_dir,
            f"{prefix}_{current_label}.txt"
        )

        with open(out_path, "w") as out:
            out.writelines(current_block)

        print(f"Wrote {out_path} ({len(current_block)} lines)")

    print(f"Total files written: {file_count + 1}")


def main():
    for cfg in configs:
        process(cfg)
    print("\nDone.")


if __name__ == "__main__":
    main()