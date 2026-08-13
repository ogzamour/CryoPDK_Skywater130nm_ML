import os
import numpy as np

def calculate_exact_paper_metrics(measured_list, modeled_list):
    """
    Computes the mathematically exact equivalents of Equations 5.1, 5.2, and 5.3
    from the paper.

    Eq. 5.1:  RRMS_k = sqrt( (1/N_k) * sum_i (I_model_i,k - I_data_i,k)^2 )
                        / ( (1/N_k) * sum_i |I_data_i,k| )

    Eq. 5.2:  mean_RRMS = (1/M) * sum_k RRMS_k

    Eq. 5.3:  sigma_RRMS = sqrt( (1/M) * sum_k (RRMS_k - mean_RRMS)^2 )
    """
    rrms_k_list = []
    M = len(measured_list)

    if M == 0:
        return 0.0, 0.0

    for k in range(M):
        meas = np.array(measured_list[k]).flatten()
        mod = np.array(modeled_list[k]).flatten()

        # Point matching/trimming adjustment
        if len(meas) != len(mod):
            print(f"    ⚠ Curve {k}: length mismatch before trim -> "
                  f"meas N={len(meas)}, mod N={len(mod)}")
            min_len = min(len(meas), len(mod))
            meas = meas[:min_len]
            mod = mod[:min_len]

        N_k = len(meas)
        if N_k == 0:
            continue

        # --- DIAGNOSTIC: magnitude / sign / scale check for this curve ---
        meas_absmax = np.max(np.abs(meas))
        mod_absmax = np.max(np.abs(mod))
        scale_ratio = mod_absmax / meas_absmax if meas_absmax != 0 else float('nan')
        print(f"    [diag] Curve {k}: meas|max|={meas_absmax:.4e}  "
              f"mod|max|={mod_absmax:.4e}  scale(mod/meas)={scale_ratio:.3f}  "
              f"meas[0:3]={meas[:3]}  mod[0:3]={mod[:3]}")

        # Equation 5.1
        numerator = np.sqrt((1.0 / N_k) * np.sum((mod - meas) ** 2))
        denominator = (1.0 / N_k) * np.sum(np.abs(meas))

        if denominator == 0:
            denominator = 1e-9

        rrms_k = numerator / denominator
        print(f"    -> Curve {k} RRMS: {rrms_k:.4f}")
        rrms_k_list.append(rrms_k)

    if not rrms_k_list:
        return 0.0, 0.0

    # Equation 5.2 & 5.3
    overall_mean_rrms = np.mean(rrms_k_list)
    population_std = np.std(rrms_k_list, ddof=0)

    return overall_mean_rrms, population_std

# --- ENVIRONMENT PATH CONFIGURATION ---
pMeas_Dir = '/home/oliviag/Skywater-130nm-77K-Cryogenic-Models/cryo_data/'
pModel_Dir = '/home/oliviag/ngspice-skywater-sims/pfet_mod/'

# Updated File Mappings matching your exact naming conventions
p_vds_pairs = [
    ('idVd_vg_0p370.txt', 'idvd_Vg-0p37.csv'),
    ('idVd_vg_0p740.txt', 'idvd_Vg-0p74.csv'),
    ('idVd_vg_1p110.txt', 'idvd_Vg-1p11.csv'),
    ('idVd_vg_1p480.txt', 'idvd_Vg-1p48.csv'),
    ('idVd_vg_1p850.txt', 'idvd_Vg-1p85.csv')
]

p_vgs_pairs = [
    ('idVg_vd_0p010.txt', 'idvg_Vd-0p01.csv'),
    ('idVg_vd_0p370.txt', 'idvg_Vd-0p37.csv'),
    ('idVg_vd_0p740.txt', 'idvg_Vd-0p74.csv'),
    ('idVg_vd_1p110.txt', 'idvg_Vd-1p11.csv'),
    ('idVg_vd_1p480.txt', 'idvg_Vd-1p48.csv'),
    ('idVg_vd_1p850.txt', 'idvg_Vd-1p85.csv')
]

# Explicit dictionary maps to prevent cross-contamination across folders
pmos_geometries = [
    {"display_name": "0.35 / 0.55", "meas_dir": "pmos_FET_len_0p35_wid_0p55", "mod_vd": "l_0p35_w_0p55/vd_sweep/", "mod_vg": "l_0p35_w_0p55/vg_sweep/"},
    {"display_name": "0.35 / 1.6",  "meas_dir": "pmos_FET_len_0.35_wid_1.6",  "mod_vd": "l_0p35_w_1p6/vd_sweep/",  "mod_vg": "l_0p35_w_1p6/vg_sweep/"},
    {"display_name": "0.35 / 5",    "meas_dir": "pmos_FET_len_0p35_wid_5",    "mod_vd": "l_0p35_w_5p0/vd_sweep/",  "mod_vg": "l_0p35_w_5p0/vg_sweep/"},
    {"display_name": "0.5 / 0.42",  "meas_dir": "pmos_FET_len_0p5_wid_0p42",  "mod_vd": "l_0p50_w_0p42/vd_sweep/", "mod_vg": "l_0p50_w_0p42/vg_sweep/"},
    {"display_name": "0.5 / 0.64",  "meas_dir": "pmos_FET_len_0p5_wid_0p64",  "mod_vd": "l_0p50_w_0p64/vd_sweep/", "mod_vg": "l_0p50_w_0p64/vg_sweep/"},
    {"display_name": "2 / 5",       "meas_dir": "pmos_FET_len_2_wid_5",       "mod_vd": "l_2p0_w_5p0/vd_sweep/",   "mod_vg": "l_2p0_w_5p0/vg_sweep/"},
    {"display_name": "4 / 7",       "meas_dir": "pmos_FET_len_4_wid_7",       "mod_vd": "l_4p0_w_7p0/vd_sweep/",   "mod_vg": "l_4p0_w_7p0/vg_sweep/"},
    {"display_name": "8 / 0.84",    "meas_dir": "pmos_FET_len_8_wid_0p84",    "mod_vd": "l_8p0_w_0p84/vd_sweep/",  "mod_vg": "l_8p0_w_0p84/vg_sweep/"},
    {"display_name": "8 / 1.6",     "meas_dir": "pmos_FET_len_8_wid_1p6",     "mod_vd": "l_8p0_w_1p6/vd_sweep/",  "mod_vg": "l_8p0_w_1p6/vg_sweep/"},
    {"display_name": "8 / 5",       "meas_dir": "pmos_FET_len_8_wid_5",       "mod_vd": "l_8p0_w_5p0/vd_sweep/",  "mod_vg": "l_8p0_w_5p0/vg_sweep/"}
]

p_RRMS_results = []

print("--- STARTING PMOS FILE LOADING AUDIT ---")
for dev in pmos_geometries:
    this_device_meas = []
    this_device_mod = []

    pathMeas = os.path.join(pMeas_Dir, dev["meas_dir"])
    pathModVd = os.path.join(pModel_Dir, dev["mod_vd"])
    pathModVg = os.path.join(pModel_Dir, dev["mod_vg"])

    vg_success_count = 0
    vd_success_count = 0

    # Process Vg loops
    for mod_f, meas_f in p_vgs_pairs:
        try:
            p_model = (np.loadtxt(os.path.join(pathModVg, mod_f), usecols=3, unpack=True))
            p_meas = (np.loadtxt(os.path.join(pathMeas, meas_f), skiprows=1, delimiter=',', usecols=2, unpack=True))
            this_device_mod.append(p_model)
            this_device_meas.append(p_meas)
            vg_success_count += 1
        except Exception as e:
            print(f"  ❌ Failed to load Vg pair: {mod_f} / {meas_f} for {dev['display_name']}. Error: {e}")

    # Process Vd loops
    for mod_f, meas_f in p_vds_pairs:
        try:
            p_model = (np.loadtxt(os.path.join(pathModVd, mod_f), usecols=3, unpack=True))
            p_meas = (np.loadtxt(os.path.join(pathMeas, meas_f), skiprows=1, delimiter=',', usecols=2, unpack=True))
            this_device_mod.append(p_model)
            this_device_meas.append(p_meas)
            vd_success_count += 1
        except Exception as e:
            print(f"  ❌ Failed to load Vd pair: {mod_f} / {meas_f} for {dev['display_name']}. Error: {e}")

    if dev['display_name'] == "0.35 / 0.55" and len(this_device_meas) > 0:
        print("\n=== 0.35 / 0.55 PEAK CURRENT DIAGNOSTIC ===")
        for idx in range(len(this_device_meas)):
            m_max = np.max(this_device_meas[idx])
            s_max = np.max(this_device_mod[idx])
            ratio = s_max / m_max if m_max != 0 else 0
            print(f"  Curve {idx}: Meas Max = {m_max:.3e} | Sim Max = {s_max:.3e} | Factor Diff = {ratio:.2f}x")
        print("============================================\n")

    total_loaded = vg_success_count + vd_success_count
    print(f"🔹 Device {dev['display_name']}: Loaded {total_loaded}/11 curves (Vg: {vg_success_count}, Vd: {vd_success_count})")

    if total_loaded > 0:
        mean_val, std_val = calculate_exact_paper_metrics(this_device_meas, this_device_mod)
        p_RRMS_results.append({'geometry': dev['display_name'], 'rrms': mean_val, 'std': std_val})

# --- PRINTING RESULTS ---
print("\n" + "="*75)
print(f"{'PMOS SKYWATER GEOMETRY':<25} | {'DEVICE MEAN RRMS':<20} | {'STD DEV (σ)':<15}")
print("="*75)
for entry in p_RRMS_results:
    print(f"{entry['geometry']:<25} | {entry['rrms']:.4f}             | {entry['std']:.4f}")
print("="*75)

p_rrms_values = [e['rrms'] for e in p_RRMS_results]
if p_rrms_values:
    print(f"{'TOTAL PMOS FRAMEWORK MEAN RRMS:':<25} | {np.mean(p_rrms_values):.4f}")
print("="*75)