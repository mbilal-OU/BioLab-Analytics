
import math

def cell_seeding_volume(target_cells, cell_density_cells_per_ml):
    if target_cells <= 0 or cell_density_cells_per_ml <= 0:
        raise ValueError("All values must be positive.")
    return target_cells / cell_density_cells_per_ml * 1000

def viability_percent(live_cells, dead_cells):
    if live_cells < 0 or dead_cells < 0:
        raise ValueError("Cell counts cannot be negative.")
    total = live_cells + dead_cells
    if total == 0:
        raise ValueError("Total cells cannot be zero.")
    return live_cells / total * 100

def population_doubling_time(time_hours, initial_cells, final_cells):
    if time_hours <= 0 or initial_cells <= 0 or final_cells <= initial_cells:
        raise ValueError("Invalid growth inputs.")
    return time_hours * math.log(2) / math.log(final_cells / initial_cells)
