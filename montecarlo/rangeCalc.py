import numpy as np
from nomSweep_latinHypercube import *
from scipy.stats import qmc


def run_sensitivity_test(param_300k):
    sensitivities = {}
    #baseline_iv = getSim(param_300k) # Baseline simulation curve
    baseIV_file = 'roomTemp_vgs.dat'
    
    for param, base_val in param_300k.items():
        if base_val == 0:
            continue
            
        # Perturb up by 10%
        perturbed_params = param_300k.copy()
        perturbed_params[param] = base_val * 1.10
        
        try:
            new_iv = simulator_func(perturbed_params)
            # Calculate max percentage change in electrical output (e.g., Id)
            delta_output = np.max(np.abs(new_iv - baseline_iv) / np.abs(baseline_iv))
            sensitivities[param] = delta_output
        except Exception:
            # If it crashes on a 10% shift, it's hyper-sensitive
            sensitivities[param] = 999.0 
            
    return sensitivities
def assign_bounds_from_sensitivity(param_300k, sensitivities):
    dynamic_bounds = {}
    
    for param, base_val in param_300k.items():
        sens_score = sensitivities.get(param, 0.1)
        
        # If a small tweak causes massive electrical changes, keep bounds tight
        if sens_score > 0.5: 
            lower = base_val * 0.50
            upper = base_val * 2.00
        # If it's a stable electrostatic parameter
        elif param in ["vth0", "eta0"]:
            lower = base_val * 0.80
            upper = base_val * 1.50
        # If it's a sluggish mathematical knob or low sensitivity, give it a wide net
        else:
            lower = base_val * 0.01
            upper = base_val * 50.0
            
        dynamic_bounds[param] = (lower, upper)
        
    return dynamic_bounds


def validate_and_refine_bounds(param_300k, dynamic_bounds, simulator_func, num_pilot_runs=50):
    param_list = list(dynamic_bounds.keys())
    lower_bounds = [dynamic_bounds[p][0] for p in param_list]
    upper_bounds = [dynamic_bounds[p][1] for p in param_list]
    
    sampler = qmc.LatinHypercube(d=len(param_list))
    sample_matrix = sampler.random(n=num_pilot_runs)
    scaled_matrix = qmc.scale(sample_matrix, np.array(lower_bounds), np.array(upper_bounds))
    
    valid_samples = []
    crashes = 0
    
    for row in scaled_matrix:
        test_params = {param_list[i]: row[i] for i in range(len(param_list))}
        try:
            # Run simulation test
            iv_curve = simulator_func(test_params)
            
            # Check for physical sanity (e.g., no NaNs, no infinite currents, reasonable on/off ratio)
            if np.isnan(iv_curve).any() or np.max(iv_curve) > 1.0: # 1.0A is arbitrary safety cap
                raise ValueError("Unphysical output")
                
            valid_samples.append(row)
        except Exception:
            crashes += 1
            
    crash_rate = crashes / num_pilot_runs
    print(f"Pilot run crash rate: {crash_rate * 100}%")
    
    # Safety feedback loop: If crash rate is too high, automatically shrink bounds inward
    if crash_rate > 0.15:
        print("Crash rate too high! Automatically tightening bounds...")
        # Recursively scale bounds closer to room temp baseline if they cause too many simulator blow-ups
        for p in dynamic_bounds:
            b_val = param_300k[p]
            old_l, old_u = dynamic_bounds[p]
            # Pull bounds 20% closer to baseline
            dynamic_bounds[p] = (b_val + (old_l - b_val) * 0.8, b_val + (old_u - b_val) * 0.8)
            
    return dynamic_bounds
    
