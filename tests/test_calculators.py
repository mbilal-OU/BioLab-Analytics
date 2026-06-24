
from biolab_analytics.calculators.solution_chemistry import mass_for_molar_solution
from biolab_analytics.calculators.dilution import c1v1
from biolab_analytics.calculators.microbiology import cfu_per_ml
from biolab_analytics.calculators.sequencing import genome_coverage

def test_molarity():
    assert round(mass_for_molar_solution(1, 1, 58.44), 2) == 58.44

def test_dilution():
    stock, diluent = c1v1(100, 1, 100)
    assert round(stock, 2) == 1.00
    assert round(diluent, 2) == 99.00

def test_cfu():
    assert cfu_per_ml(120, 1e-6, 0.1) == 1.2e9

def test_coverage():
    assert genome_coverage(1_000_000, 150, 5_000_000) == 30
