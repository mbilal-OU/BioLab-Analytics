import pytest
from labcalc.cli import (
    ureg,
    calc_dilution,
    calc_stock_to_working,
    calc_grams_for_molar_solution,
    calc_percent_solution,
)

def test_dilution_basic():
    c1 = ureg.Quantity("10 mM")
    c2 = ureg.Quantity("1 mM")
    v2 = ureg.Quantity("50 mL")
    res = calc_dilution(c1, c2, v2)
    # V1 = (1/10)*50 mL = 5 mL
    assert pytest.approx(res.v1.to("mL").magnitude, rel=1e-9) == 5.0
    assert pytest.approx(res.v_diluent.to("mL").magnitude, rel=1e-9) == 45.0

def test_stock_to_working_10x_to_1x():
    v2 = ureg.Quantity("500 mL")
    res = calc_stock_to_working(10, 1, v2)
    assert pytest.approx(res.v_stock.to("mL").magnitude, rel=1e-9) == 50.0
    assert pytest.approx(res.v_diluent.to("mL").magnitude, rel=1e-9) == 450.0

def test_molarity_tris_1M_100mL():
    M = ureg.Quantity("1 M")
    V = ureg.Quantity("100 mL")
    res = calc_grams_for_molar_solution(121.14, M, V)
    # 1 mol/L * 0.1 L * 121.14 = 12.114 g
    assert pytest.approx(res.grams.to("g").magnitude, rel=1e-9) == 12.114

def test_percent_wv_10pct_100mL():
    V = ureg.Quantity("100 mL")
    res = calc_percent_solution("wv", 10, V)
    assert pytest.approx(res.solute_amount.to("g").magnitude, rel=1e-9) == 10.0

def test_percent_vv_70pct_500mL():
    V = ureg.Quantity("500 mL")
    res = calc_percent_solution("vv", 70, V)
    assert pytest.approx(res.solute_amount.to("mL").magnitude, rel=1e-9) == 350.0
    assert pytest.approx(res.diluent_volume.to("mL").magnitude, rel=1e-9) == 150.0
