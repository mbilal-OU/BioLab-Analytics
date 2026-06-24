
import math

def cfu_per_ml(colonies, dilution_fraction, plated_volume_ml):
    if colonies <= 0 or dilution_fraction <= 0 or plated_volume_ml <= 0:
        raise ValueError("All values must be positive.")
    return colonies / (dilution_fraction * plated_volume_ml)

def growth_rate(od_initial, od_final, time_hours):
    if od_initial <= 0 or od_final <= 0 or time_hours <= 0:
        raise ValueError("All values must be positive.")
    return math.log(od_final / od_initial) / time_hours

def doubling_time(growth_rate_per_hour):
    if growth_rate_per_hour <= 0:
        raise ValueError("Growth rate must be positive.")
    return math.log(2) / growth_rate_per_hour
