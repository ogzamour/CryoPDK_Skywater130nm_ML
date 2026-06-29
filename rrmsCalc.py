import os
import numpy as np
#//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
ashish_dir = '/home/oliviag/ngspice-skywater-sims/outside_data/'
pMeas_Dir = '/home/oliviag/Skywater-130nm-77K-Cryogenic-Models/cryo_data/'
pSim_Dir = '/home/oliviag/ngspice-skywater-sims/pfet_mod/'
nSim_Dir = '/home/oliviag/ngspice-skywater-sims/nfet_mod/'
#//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
pmos_geometries = [
    {"display_name": "L=0.35u W=0.55u", "meas_dir": "pmos_FET_len_0p35_wid_0p55", "mod_vd": "l_0p35_w_0p55/vd_sweep/", "mod_vg": "l_0p35_w_0p55/vg_sweep/", "vg_floor": 1e-10, "vd_floor": 0},
    {"display_name": "L=0.35u W=1.6u",  "meas_dir": "pmos_FET_len_0.35_wid_1.6",  "mod_vd": "l_0p35_w_1p6/vd_sweep/",  "mod_vg": "l_0p35_w_1p6/vg_sweep/", "vg_floor": 6e-10, "vd_floor": 0}, #6e-10
    {"display_name": "L=0.35u W=5u",    "meas_dir": "pmos_FET_len_0p35_wid_5",    "mod_vd": "l_0p35_w_5p0/vd_sweep/",  "mod_vg": "l_0p35_w_5p0/vg_sweep/", "vg_floor": 6e-6, "vd_floor": 1e-7}, #6e-6 1e-7
    {"display_name": "L=0.5u W=0.42u",  "meas_dir": "pmos_FET_len_0p5_wid_0p42",  "mod_vd": "l_0p50_w_0p42/vd_sweep/", "mod_vg": "l_0p50_w_0p42/vg_sweep/", "vg_floor": 1e-7, "vd_floor": 5e-8}, #1e-7 5e-8
    {"display_name": "L=0.5u W=0.64u",  "meas_dir": "pmos_FET_len_0p5_wid_0p64",  "mod_vd": "l_0p50_w_0p64/vd_sweep/", "mod_vg": "l_0p50_w_0p64/vg_sweep/", "vg_floor": 0, "vd_floor": 0},
    {"display_name": "L=2u W=5u",       "meas_dir": "pmos_FET_len_2_wid_5",       "mod_vd": "l_2p0_w_5p0/vd_sweep/",   "mod_vg": "l_2p0_w_5p0/vg_sweep/", "vg_floor": 6e-10, "vd_floor": 0},
    {"display_name": "L=4u W=7u",       "meas_dir": "pmos_FET_len_4_wid_7",       "mod_vd": "l_4p0_w_7p0/vd_sweep/",   "mod_vg": "l_4p0_w_7p0/vg_sweep/", "vg_floor": 1.2e-9, "vd_floor": 0.75},
    {"display_name": "L=8u W=0.84u",    "meas_dir": "pmos_FET_len_8_wid_0p84",    "mod_vd": "l_8p0_w_0p84/vd_sweep/",  "mod_vg": "l_8p0_w_0p84/vg_sweep/", "vg_floor": 1.8e-9, "vd_floor": 0},
    {"display_name": "L=8u W=1.6u",     "meas_dir": "pmos_FET_len_8_wid_1p6",     "mod_vd": "l_8p0_w_1p6/vd_sweep/",  "mod_vg": "l_8p0_w_1p6/vg_sweep/", "vg_floor": 1e-9, "vd_floor": 0},
    {"display_name": "L=8u W=5u",       "meas_dir": "pmos_FET_len_8_wid_5",       "mod_vd": "l_8p0_w_5p0/vd_sweep/",  "mod_vg": "l_8p0_w_5p0/vg_sweep/", "vg_floor": 4.5e-9, "vd_floor": 0}
]

nmos_geometries = [
    {"display_name": "L=0.15u W=1.6u", "meas_dir": "nmos_FET_len_0p15_wid_1p6", "mod_vd": "l_0p15_w_1p6/vd_sweep/", "mod_vg": "l_0p15_w_1p6/vg_sweep/"},
    {"display_name": "L=0.19u W=7u", "meas_dir": "nmos_FET_len_0p19_wid_7", "mod_vd": "l_0p19_w_7p0/vd_sweep/", "mod_vg": "l_0p19_w_7p0/vg_sweep/"},
    {"display_name": "L=0.25u W=1.6u", "meas_dir": "nmos_FET_len_0p25_wid_1p6", "mod_vd": "l_0p25_w_1p6/vd_sweep/", "mod_vg": "l_0p25_w_1p6/vg_sweep/"},
    {"display_name": "L=1u W=1.6u", "meas_dir": "nmos_FET_len_1_wid_1p6", "mod_vd": "l_1p0_w_1p6/vd_sweep/", "mod_vg": "l_1p0_w_1p6/vg_sweep/"},
    {"display_name": "L=1u W=3u", "meas_dir": "nmos_FET_len_1_wid_3", "mod_vd": "l_1p0_w_3p0/vd_sweep/", "mod_vg": "l_1p0_w_3p0/vg_sweep/"},
    {"display_name": "L=8u W=1.6u", "meas_dir": "nmos_FET_len_8_wid_1.6", "mod_vd": "l_8p0_w_1p6/vd_sweep/", "mod_vg": "l_8p0_w_1p6/vg_sweep/"},
    {"display_name": "L=20u W=0.64u", "meas_dir": "nmos_FET_len_20_wid_0p64", "mod_vd": "l_20p0_w_0p64/vd_sweep/", "mod_vg": "l_20p0_w_0p64/vg_sweep/"},
    {"display_name": "L=100u W=100u", "meas_dir": "nmos_FET_len_100_wid_100", "mod_vd": "l_100p0_w_100p0/vd_sweep/", "mod_vg": "l_100p0_w_100p0/vg_sweep/"}
    
]


# --- FILE SUB-PAIRS ---
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

n_vds_pairs = [
    ('idVd_vg_0p370.txt', 'idvd_Vg0p37.csv'),
    ('idVd_vg_0p740.txt', 'idvd_Vg0p74.csv'),
    ('idVd_vg_1p110.txt', 'idvd_Vg1p11.csv'),
    ('idVd_vg_1p480.txt', 'idvd_Vg1p48.csv'),
    ('idVd_vg_1p850.txt', 'idvd_Vg1p85.csv')
]

n_vgs_pairs = [
    ('idVg_vd_0p010.txt', 'idvg_Vd0p01.csv'),
    ('idVg_vd_0p370.txt', 'idvg_Vd0p37.csv'),
    ('idVg_vd_0p740.txt', 'idvg_Vd0p74.csv'),
    ('idVg_vd_1p110.txt', 'idvg_Vd1p11.csv'),
    ('idVg_vd_1p480.txt', 'idvg_Vd1p48.csv'),
    ('idVg_vd_1p850.txt', 'idvg_Vd1p85.csv')
]
ashish = [
    ("idVg_vd_0p000.txt", 'idvg_Vd-0p01.csv', 'idVg_vd_0p010.txt'),
    ("idVg_vd_0p370.txt", 'idvg_Vd-0p37.csv', 'idVg_vd_0p370.txt'),
    ("idVg_vd_0p740.txt", 'idvg_Vd-0p74.csv', 'idVg_vd_0p740.txt'),
    ("idVg_vd_1p110.txt", 'idvg_Vd-1p11.csv', 'idVg_vd_1p110.txt'),
    ("idVg_vd_1p480.txt", 'idvg_Vd-1p48.csv', 'idVg_vd_1p480.txt' )
]

#//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
def curveRRMS(I_measTot, I_simTot):
    RRMS_numSum = 0
    RRMS_denSum = 0
    N = len(I_measTot)
    
    rmse = np.sqrt(np.mean((I_simTot - I_measTot) ** 2))
    mean_meas = np.mean(np.abs(I_measTot))
    #RRMS_k = rmse / mean_meas
    '''if mean_meas <= 0 : #5e-10: 3.229e-7
        RRMS_k = 0
        print(f"mean meas: {mean_meas}")
    else:
        RRMS_k = rmse / mean_meas'''
    RRMS_k = rmse / mean_meas
    
    return RRMS_k
#//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
def getVth(filePath, simFile):
    vth_col = np.loadtxt(os.path.join(filePath, simFile), usecols=5, unpack=True)
    vth = vth_col[0]
    return vth
#//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
def cleanCurrent(i_meas):  
    try:
        zero_idx = next(i for i in range(len(i_meas) - 1, -1, -1) if i_meas[i] == 0)
        #print("Last zero index:", zero_idx)
        j = 0
        while j < zero_idx:
            #print(f"iteration {j}")
            if i_meas[j] != 0:
                i_meas[j] = 0
            j += 1
    except StopIteration:
        print("No zeros found in the array.")
    return i_meas
#//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
def p_loadCurrentVals(sim_path, meas_path, vth, sim_cols, meas_cols, meas_skip):
    # Load simulation: col 5 is voltage, col 3 is Id
    sim_data = np.loadtxt(sim_path, usecols=sim_cols, unpack=True)
    v_sim, i_sim = sim_data[0], sim_data[1]

    # Load measurement: meas_cols[0] is voltage, meas_cols[1] is Id
    meas_data = np.loadtxt(
        meas_path,
        skiprows=meas_skip,
        delimiter=",",
        usecols=meas_cols,
        unpack=True,
    )
    v_meas, i_meas = meas_data[0], meas_data[1] #_raw
    #i_meas = cleanCurrent(i_meas_raw)
    #sim_start_idx = np.argmax(v_sim >= vth)
    #meas_start_idx = np.argmax(v_meas >= vth)
    if np.abs(v_meas[-1]) >= vth:
        start_idx = np.argmax(np.abs(v_meas) >= vth)
        print(f"start_index = {start_idx}")
    #start_idx = np.argmax(np.abs(i_meas) > vth)
    #if start_idx == 0:
       # start_idx = np.argmax(i_sim > 0)
        print(f"start_index = {start_idx}")
    #print(f"starting v: meas = {v_meas[start_idx]}, sim = {v_sim[start_idx]}")

    #filtered_i_sim = i_sim[sim_start_idx:]
    #filtered_i_meas = i_meas[meas_start_idx:]
        filtered_i_sim = i_sim[start_idx:]
        filtered_i_meas = i_meas[start_idx:]

        min_len = min(len(filtered_i_sim), len(filtered_i_meas))

        return filtered_i_sim[:min_len], filtered_i_meas[:min_len]
    else:
        return [0], [0]
#//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
def loadCurrentVals(sim_path, meas_path, vth, sim_cols, meas_cols, meas_skip):
    # Load simulation: col 5 is voltage, col 3 is Id
    sim_data = np.loadtxt(sim_path, usecols=sim_cols, unpack=True)
    v_sim, i_sim = sim_data[0], sim_data[1]

    # Load measurement: meas_cols[0] is voltage, meas_cols[1] is Id
    meas_data = np.loadtxt(
        meas_path,
        skiprows=meas_skip,
        delimiter=",",
        usecols=meas_cols,
        unpack=True,
    )
    v_meas, i_meas_raw = meas_data[0], meas_data[1]

    i_meas = cleanCurrent(i_meas_raw)
    start_idx = np.argmax(np.abs(i_meas) > vth)
    print(f"start_index = {start_idx}")


   
    filtered_i_sim = i_sim[start_idx:]
    filtered_i_meas = i_meas[start_idx:]

    min_len = min(len(filtered_i_sim), len(filtered_i_meas))

    return filtered_i_sim[:min_len], filtered_i_meas[:min_len]
#//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
#PMOS
dev_rrmsK = []
dev_sig = []
for device in pmos_geometries:
    device_simI = []
    device_measI = []
    #dev_meas = []
    #dev_sim = []
    #dev_rrmsK = []
    rrmsK_curves = []
    p_meas = os.path.join(pMeas_Dir, device["meas_dir"])
    p_simVD = os.path.join(pSim_Dir, device["mod_vd"])
    p_simVG = os.path.join(pSim_Dir, device["mod_vg"])
    vg_th = device["vg_floor"]
    vd_th = device["vd_floor"]
    print('\n')
    print(device["display_name"])
    for vdSimFile, vdMeasFile in p_vds_pairs:
        col_s = (0,3)
        col_m = (0,2)
        simPathVD = os.path.join(p_simVD, vdSimFile)
        mPathVD = os.path.join(p_meas, vdMeasFile)
        #i_on = 1.5e-6
        I_simVD, I_measVD = loadCurrentVals(simPathVD, mPathVD, vd_th, col_s, col_m, 1)
        #I_simVD, I_measVD = p_loadCurrentVals(simPathVD, mPathVD, vd_vth, col_s, col_m, 1)
        #if len(I_simVD) > 1:
        if np.mean(np.abs(I_measVD)) > 0:
            if np.abs(I_simVD[-1]) > 1e-10:
                print(np.mean(np.abs(I_measVD)))
                vd_rrms = curveRRMS(I_measVD, I_simVD)
                print(f"{vdSimFile} rrms: {vd_rrms}")
                rrmsK_curves.append(vd_rrms)
        #vd_rrms = curveRRMS(I_measVD, I_simVD)
        #rrmsK_curves.append(vd_rrms)
        #I_simVD = np.loadtxt(os.path.join(p_simVD, vdSimFile), usecols=3, unpack=True)
        #device_simI.append(I_simVD)
        #I_measVD = np.loadtxt(os.path.join(p_meas, vdMeasFile), skiprows=1, delimiter=',', usecols=2, unpack=True)
       # vd_rrms = curveRRMS(I_measVD, I_simVD)
       # device_measI.append(I_measVD)
        #rrmsK_curves.append(vd_rrms)
    for vgSimFile, vgMeasFile in p_vgs_pairs:
       
        col_s = (0,3)
        col_m = (1,2)
        simPathVG = os.path.join(p_simVG, vgSimFile)
        mPathVG = os.path.join(p_meas, vgMeasFile)
        id_on = 1.5e-6
        I_simVG, I_measVG = loadCurrentVals(simPathVG, mPathVG, vg_th, col_s, col_m, 1)
        #I_simVG, I_measVG = p_loadCurrentVals(simPathVG, mPathVG, vg_vth, col_s, col_m, 1)
        if np.mean(np.abs(I_measVG)) > 0:
        #if len(I_simVG) > 1:
            if np.abs(I_simVG[-1]) > 1e-11:
                print(np.mean(np.abs(I_measVG)))
                vg_rrms = curveRRMS(I_measVG, I_simVG)
                print(f"{vgSimFile} rrms: {vg_rrms}")
                rrmsK_curves.append(vg_rrms)
        
        #vg_rrms = curveRRMS(I_measVG, I_simVG)
        #rrmsK_curves.append(vg_rrms)
        #I_simVG = np.loadtxt(os.path.join(p_simVG, vgSimFile), usecols=3, unpack=True)
        #device_simI.append(I_simVG)
        #I_measVG = np.loadtxt(os.path.join(p_meas, vgMeasFile), skiprows=1, delimiter=',', usecols=2, unpack=True)
        #device_measI.append(I_measVG)
       # vg_rrms = curveRRMS(I_measVG, I_simVG)
        #rrmsK_curves.append(vg_rrms)
    dSquared = []
    #rrmse_now = deviceGlobalRRMSE(device_measI, device_simI)
    
    device_rrms = np.mean(rrmsK_curves)
    print(device_rrms)
    deviceRRMS = np.mean(rrmsK_curves)
    dev_rrmsK.append(deviceRRMS)
    for rrmsK in rrmsK_curves:
        underRoot = np.power((rrmsK - device_rrms), 2)
        dSquared.append(underRoot)
    sigma = np.sqrt(np.mean(dSquared))
    dev_sig.append(sigma)
print(dev_rrmsK)
print(f"\n{'Device Geometry':<25} | {'Device RRMSk':<20} | {'STD DEV (σ)':<15}")
for dev, rrmsk, sigma in zip(pmos_geometries, dev_rrmsK, dev_sig):
    name = dev['display_name']
    print(f"{name:<25} | {rrmsk:<20.4f} | {sigma:<15.4f}")
rrms_TOT = np.mean(dev_rrmsK)
sig_TOT = np.mean(dev_sig)
print(f"Total PMOS RRMS: {rrms_TOT}")
print(f"Total PMOS Std Dev: {sig_TOT}") 

#//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
#NMOS
n_dev_rrmsK = []
n_dev_sig = []
for device in nmos_geometries:
    device_simI = []
    device_measI = []
    #dev_meas = []
    #dev_sim = []
    #dev_rrmsK = []
    rrmsK_curves = []
    p_meas = os.path.join(pMeas_Dir, device["meas_dir"])
    n_simVD = os.path.join(nSim_Dir, device["mod_vd"])
    n_simVG = os.path.join(nSim_Dir, device["mod_vg"])
    print(device["display_name"])
    for vdSimFile, vdMeasFile in n_vds_pairs:
        vth = 0 #getVth(n_simVD, vdSimFile)
        col_s = (0,3)
        col_m = (0,2)
        
        simPathVD = os.path.join(n_simVD, vdSimFile)
        mPathVD = os.path.join(p_meas, vdMeasFile)
        I_simVD, I_measVD = loadCurrentVals(simPathVD, mPathVD, vth, col_s, col_m, 1)
        if np.mean(np.abs(I_measVD)) > 3e-7:
            if device["meas_dir"] == "nmos_FET_len_100_wid_100":
                #print(np.mean(I_measVD))
                if np.mean(np.abs(I_measVD)) > 3e-5:
                #if vdSimFile != 'idVd_vg_0p370.txt':
                    vd_rrms = curveRRMS(I_measVD, I_simVD)
                    #print(f"{vdSimFile} rrms: {vd_rrms}")
                    rrmsK_curves.append(vd_rrms)
            else:
                vd_rrms = curveRRMS(I_measVD, I_simVD)
                #print(f"{vdSimFile} rrms: {vd_rrms}")
                rrmsK_curves.append(vd_rrms)

    for vgSimFile, vgMeasFile in n_vgs_pairs:
        vth = 0 #getVth(n_simVG, vgSimFile)
        col_s = (0,3)
        col_m = (1,2)

        simPathVG = os.path.join(n_simVG, vgSimFile)
        mPathVG = os.path.join(p_meas, vgMeasFile)
        I_simVG, I_measVG = loadCurrentVals(simPathVG, mPathVG, vth, col_s, col_m, 1)
            
        if np.mean(np.abs(I_measVG)) > 2e-7:
            if device["meas_dir"] == "nmos_FET_len_100_wid_100":
                #print(np.mean(I_measVG))
                if np.mean(np.abs(I_measVG)) > 9e-10:
                    vg_rrms = curveRRMS(I_measVG, I_simVG)
                    #print(f"{vgSimFile} rrms: {vg_rrms}")
                    rrmsK_curves.append(vg_rrms)
            else:
                vg_rrms = curveRRMS(I_measVG, I_simVG)
                #print(f"{vgSimFile} rrms: {vg_rrms}")
                rrmsK_curves.append(vg_rrms)
    #rrmse_now = deviceGlobalRRMSE(device_measI, device_simI)
    dSquared = []
    device_rrms = np.mean(rrmsK_curves)
    print(device_rrms)
    deviceRRMS = np.mean(rrmsK_curves)
    n_dev_rrmsK.append(deviceRRMS)
    for rrmsK in rrmsK_curves:
        underRoot = np.power((rrmsK - device_rrms), 2)
        dSquared.append(underRoot)
    sigma = np.sqrt(np.mean(dSquared))
    n_dev_sig.append(sigma)

print(n_dev_rrmsK)
print(f"\n{'Device Geometry':<25} | {'Device RRMSk':<20} | {'STD DEV (σ)':<15}")
for dev, rrmsk, sigma in zip(nmos_geometries, n_dev_rrmsK, n_dev_sig):
    name = dev['display_name']
    print(f"{name:<25} | {rrmsk:<20.4f} | {sigma:<15.4f}")
nmos_rrms_TOT = np.mean(n_dev_rrmsK)
nmos_sig_TOT = np.mean(n_dev_sig)
print(f"Total NMOS RRMS: {nmos_rrms_TOT}")
print(f"Total NMOS Std Dev: {nmos_sig_TOT}")

#//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
#combination
final_rrms = (nmos_rrms_TOT + rrms_TOT) / 2
print(f"Final Combined RRMS: {final_rrms}")
final_sig = (nmos_sig_TOT + sig_TOT) / 2
print(f"Final Combined Sigma: {final_sig}")


'''hDev = nmos_geometries[0]
hMeasFile = hDev["meas_dir"]
hMeasPath = os.path.join(pMeas_Dir, hMeasFile)
hVdFile = 'idvg_Vd1p48.csv' 
hCompFile = '/home/oliviag/ngspice-skywater-sims/outside_data/hspice.csv'
I_hspice = np.loadtxt(hCompFile, skiprows=1, delimiter=',', usecols=1, unpack=True)
I_compMeas = np.loadtxt(os.path.join(hMeasPath, hVdFile), skiprows=63, delimiter=',', usecols=2, unpack=True)

hspice_rrms = curveRRMS(I_compMeas, np.abs(I_hspice))
dName = hDev['display_name']
print(f"HSpice RRMS {dName}: {hspice_rrms}")'''



'''
ash_m_Curves = []
o_m_curve = []
a_o_curve = []
for curve, measC, oliviaC in ashish:
    measD = os.path.join(pMeas_Dir, 'pmos_FET_len_0.35_wid_1.6')
    oliviaDir = os.path.join(pSim_Dir, 'l_0p35_w_1p6/vg_sweep/')
    aSim = np.loadtxt(os.path.join(ashish_dir, curve), usecols=5, unpack=True)
    oSim = np.loadtxt(os.path.join(oliviaDir, oliviaC), usecols=3, unpack=True)
    comp = np.loadtxt(os.path.join(measD, measC), skiprows=1, delimiter=',', usecols=2, unpack=True)
    print('ashish meas')
    rrms_a_meas = curveRRMS(comp, aSim)
    ash_m_Curves.append(rrms_a_meas)
    print('olivia meas')
    rrms_o_meas = curveRRMS(comp, oSim)
    o_m_curve.append(rrms_o_meas)
    print('ashish olivia')
    rrms_a_o = (np.abs(aSim), np.abs(oSim))
    a_o_curve.append(rrms_a_o)
a_totalRRMS = np.mean(ash_m_Curves)
print(f"ashsish compared to measurment rrms; {a_totalRRMS}")
o_totalRRMS = np.mean(o_m_curve)
print(f"olivia compared to measurement rrms; {o_totalRRMS}")
compRRMS = np.mean(a_o_curve)
print(f"olivia compared to ashish rrms; {compRRMS}")'''
   