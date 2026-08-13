import os
import subprocess
from pathlib import Path

# =========================
# GEOMETRIES
# =========================


def buildNetlist(circuit, device):
    home = Path.home()
    mainDir = Path.home() / "ngspice-skywater-sims/pfet_mod/"
    #devDir = os.path.join(mainDir, f'{device}')
    mainPath = Path(mainDir)
    vds_file = mainPath / f'{device}/vd_sweep/p_vds_sweep_family.txt'
   
    vgs_file = mainPath / f'{device}/vg_sweep/p_vgs_sweep_family.txt'
 
    vgs_single_file = mainPath / f'{device}/vg_sweep/idVg_vd_0p010.txt'

    biasV = -1.48
    for target_file in [vds_file, vgs_file, vgs_single_file]:
          if target_file.exists():
            target_file.unlink()
    vgs_single_file.touch()
    vgs_file.touch()
    vds_file.touch()
    
    
    device_cmd = f"""* PMOS sweep (Sky130) 
.lib "/home/oliviag/skywater130nm/volare/sky130/versions/a918dc7c8e474a99b68c85eb3546b4ed91fe9e7b/sky130A/libs.tech/ngspice/sky130.lib.spice" tt_77k
{circuit} nf=1 ad='floor((nf+1)/2) * w/nf * 0.29' as='floor((nf+2)/2) * w/nf * 0.29' pd='2 * floor((nf+1)/2) * (w/nf + 0.29)' ps='2 * floor((nf+2)/2) * (w/nf + 0.29)' nrd='0.29 / w' nrs='0.29 / w' sa=0 sb=0 sd=0 

Vgs gate GND 0
Vds VDD GND -1.48
.temp -196.15
"""
    
    control_lines = [
    ".control",
    "set noaskquit",
    "set filetype=ascii",
    "run",
    ]
    control_lines.extend(
    [
        'dc Vds 0 -1.85 -0.01 Vgs 0 -1.85 -0.37',
        'showmod m.xm1.msky130_fd_pr__pfet_01v8_lvt : vth0 u0 rdsw nfactor vsat eta0 delta',
        'setplot',
        'display',
        'shell pwd',
        'let ax_id0 = -vds#branch',
        'set wr_singlescale',
        f'wrdata {vds_file} vdd gate ax_id0',
        'reset',
    ])

    control_lines.extend(
    [
        'dc Vgs 0 -1.85 -0.01  Vds 0 -1.85 -0.37',
        'let ax_id2 = -vds#branch',
        f'wrdata {vgs_file} vdd gate ax_id2',
        'reset',
        
    ])
    control_lines.extend(
    [
        'alter Vds -0.01',
        'dc Vgs 0 -1.85 -0.01',
        'let ax_id1 = -vds#branch',
        f'wrdata {vgs_single_file} vdd gate ax_id1',
        
    ])
    control_lines.extend(["quit", ".endc", ".end"])
    
    with open("dev_sweep.spice", "w+") as f:
    # Pre-read the base template so you don't read it from disk over and over
        #base_template = open(SPICE_FILE).read()
        #print ('opened')


        f.seek(0)    
        f.truncate()  
        f.write(device_cmd)
        f.write("\n\n")
        f.write("\n".join(control_lines))
        f.flush()     
    logFile = os.path.join(mainDir, f"{device}/dev_sweep.log")
    with open(logFile, 'w') as log:
        subprocess.run(["ngspice", "-b","-q", "dev_sweep.spice"], stdout=log, stderr=subprocess.STDOUT)#, capture_output=True, text=True)
    return

    