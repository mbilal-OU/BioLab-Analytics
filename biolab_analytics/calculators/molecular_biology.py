
AVOGADRO = 6.02214076e23

def dna_copy_number(dna_mass_ng, length_bp):
    if dna_mass_ng <= 0 or length_bp <= 0:
        raise ValueError("All values must be positive.")
    mass_g = dna_mass_ng * 1e-9
    molecular_weight = length_bp * 660
    return (mass_g / molecular_weight) * AVOGADRO

def pcr_mastermix(reactions, extra_percent, components):
    if reactions < 1 or extra_percent < 0:
        raise ValueError("Invalid PCR inputs.")
    multiplier = reactions * (1 + extra_percent / 100)
    return [
        {
            "component": name,
            "per_reaction_ul": volume,
            "total_ul": volume * multiplier
        }
        for name, volume in components.items()
    ]
