
def c1v1(stock_concentration, final_concentration, final_volume):
    if stock_concentration <= 0 or final_concentration <= 0 or final_volume <= 0:
        raise ValueError("All values must be positive.")
    if final_concentration > stock_concentration:
        raise ValueError("Final concentration cannot exceed stock concentration.")
    stock_volume = final_concentration * final_volume / stock_concentration
    diluent_volume = final_volume - stock_volume
    return stock_volume, diluent_volume

def serial_dilution(start_concentration, dilution_factor, steps):
    if start_concentration <= 0 or dilution_factor <= 1 or steps < 1:
        raise ValueError("Invalid dilution inputs.")
    rows = []
    concentration = start_concentration
    for step in range(steps + 1):
        rows.append({
            "step": step,
            "dilution": f"1/{dilution_factor ** step:g}",
            "concentration": concentration
        })
        concentration /= dilution_factor
    return rows
