
def mass_for_molar_solution(molarity_m, volume_l, molecular_weight_g_per_mol):
    if molarity_m <= 0 or volume_l <= 0 or molecular_weight_g_per_mol <= 0:
        raise ValueError("All values must be positive.")
    return molarity_m * volume_l * molecular_weight_g_per_mol

def molarity_from_mass(mass_g, volume_l, molecular_weight_g_per_mol):
    if mass_g <= 0 or volume_l <= 0 or molecular_weight_g_per_mol <= 0:
        raise ValueError("All values must be positive.")
    return mass_g / (molecular_weight_g_per_mol * volume_l)

def percent_wv_mass(percent_wv, final_volume_ml):
    if percent_wv <= 0 or final_volume_ml <= 0:
        raise ValueError("All values must be positive.")
    return percent_wv * final_volume_ml / 100

def percent_vv_volume(percent_vv, final_volume_ml):
    if percent_vv <= 0 or final_volume_ml <= 0:
        raise ValueError("All values must be positive.")
    return percent_vv * final_volume_ml / 100
