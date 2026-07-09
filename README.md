# CryoPDK_Skywater130nm_ML
NGSpice simulation using translated cryogenic PDk models based on https://github.com/UTA-Advanced-Detector-Technologies/Skywater-130nm-77K-Cryogenic-Models/tree/main 

***download this repo to ngspice-skywater-sims directory in your home directory***
## Downloading_Volare

First, ensure Volare is properly set up (I did this by creating a seperate file titled skywater130nm where I placed all the things downloaded from volare (which should be 3 top files: volare, sky130A, sky130B.) 
My path essentially looked like /home/<user>/skywater130nm/volare...)

To download volare, I used the following (with <desired_PDK_directory> = skywater130nm):

```
#Taken from original cryo repo

pip install volare

export PDK_ROOT="/home/<your_username>/<desired_PDK_directory>"

volare ls-remote --pdk sky130

volare enable --pdk sky130 a918dc7c8e474a99b68c85eb3546b4ed91fe9e7b
```

## Downloading_Ngspice

I used jupyter notebooks for this, so that is the setup I will show. However, just make sure version 41 of ngspice is installed and it should work.
This is the setup I used, and I just made sure sims were run in spice_env:
```
  conda activate spice_env
  conda install -c conda-forge ngspice=41
  which ngspice
  ngspice --version
```

## Enviornment_Setup
In order to correctly set up the 77k nfet file to work with the rest of volare, you will want to place sky130_fd_pr__nfet_01v8_lvt__tt_77k.corner.spice in the following directory:
```
skywater130nm/volare/sky130/versions/a918dc7c8e474a99b68c85eb3546b4ed91fe9e7b/sky130A/libs.ref/sky130_fd_pr/spice
```
***Use the original, non translated file versions in compressed-cryo-files. Just make sure to change the .lib file as described. The translated file version is not necessary.***

Once the correct nfet file has been placed in the directory, you will want to update the sky130.lib.spice file (/home/<user>/skywater130nm/volare/sky130/versions/a918dc7c8e474a99b68c85eb3546b4ed91fe9e7b/sky130A/libs.tech/ngspice/sky130.lib.spice)
To do this, insert the following code in sky130.lib.spice under '******* SkyWater sky130 model library *********':

```
* Typical corner (tt) at 77K
.lib tt_77k
.param mc_mm_switch=0
.param mc_pr_switch=0
.param my_gauss = 0
.param m = 1
.include "/home/<user>/skywater130nm/volare/sky130/versions/a918dc7c8e474a99b68c85eb3546b4ed91fe9e7b/sky130A/libs.ref/sky130_fd_pr/spice/sky130_fd_pr__nfet_01v8_lvt__tt_77k.corner.spice"
*.include "/home/<user>/skywater130nm/volare/sky130/versions/a918dc7c8e474a99b68c85eb3546b4ed91fe9e7b/sky130A/libs.ref/sky130_fd_pr/spice/pfet_01v8_lvt/77k_models/sky130_fd_pr__pfet_01v8_lvt__tt_77k.corner.spice"

.include "/home/<user>/skywater130nm/volare/sky130/versions/a918dc7c8e474a99b68c85eb3546b4ed91fe9e7b/sky130A/libs.ref/sky130_fd_pr/spice/sky130_fd_pr__nfet_01v8_lvt__mismatch.corner.spice"
*.include "/home/<user>/skywater130nm/volare/sky130/versions/a918dc7c8e474a99b68c85eb3546b4ed91fe9e7b/sky130A/libs.ref/sky130_fd_pr/spice/pfet_01v8_lvt/sky130_fd_pr__pfet_01v8_lvt__mismatch.corner.spice"

.include "r+c/res_typical__cap_typical.spice"
.include "r+c/res_typical__cap_typical__lin.spice"

* Special cells
.include "corners/tt/specialized_cells.spice"


.endl
```
(To use pfet, delete '*' in front of the include statements)

After this, to use the pdk at 77k, just change the .lib declaration in the ngspice simulation files from tt to tt_77k!

## Running_NGSpice_Sims

The ngspice simulation can be run just from the terminal. Inside the pfet/nfet mod folder in the repo, you can use ```runAll.py```
For pfet, ensure the updated model file in this repo is inserted into the correct corner directory where the original 77k pfet model card is.

These can be run by typing ```ngspice -b <desiredSimFile>.spice``` in the terminal while in the simulation directory. 

(note: if you set ngspice in a specific enviornment like spice_env, make sure it is active while trying to run the simulation)


## RRMS

To get the RRMS calculation for the scripts, first ensure you have the cryo_data file from the paper repo downloaded. Also ensure both the nfet and pfet 77k corners are installed properly and defined in the .lib file.
Then, run ```python runAll.py``` in both the nfet_mod and pfet_mod directories ***Note: will have to change path in the .include***

After both are run, ensure the paths in getRMS.py match your directory (for both the cryo data and modeled pfet/nfet data). Then, run ```python rrmsCalc.py``` in the ngspice-skywater-sims directory and the RRMS should print in terminal.

***could also choose to not rerun pfet/nfet models since the output files are included already in repo***


## Montecarlo
To run a montecarlo simulation for all parameters on all device, run ```python nomSweep_latinHypercube.py``` in the montecarlo directory. The output will be in ```mc_output_lhc``` and all sweep data will be in 2 CSV files per parameter sweep.

  
