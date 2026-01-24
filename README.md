# Bio Lab Calc (Phase 1: Liquids)

Author: **MBILAL**

A free, open-source toolkit for common biology wet-lab calculations designed for students:
- Dilutions (C1V1=C2V2)
- X stock to working solution
- Serial dilution tables
- Molarity from powder (MW-based)
- Percent solutions (w/v, v/v)
- Excel export for lab notebook / teaching labs

## Installation

```bash
git clone <YOUR_REPO_URL>
cd bio-lab-calc
python -m venv .venv
# Linux/WSL/Mac:
source .venv/bin/activate
# Windows PowerShell:
# .\.venv\Scripts\Activate.ps1
pip install -r requirements.txt

Usage (CLI)
1) Single dilution (C1V1=C2V2)

python -m labcalc.cli dilute --c1 "10 mM" --c2 "1 mM" --v2 "50 mL" --export dilution.xlsx

2) Stock-to-working

python -m labcalc.cli stock-to-working --stock "10X" --final "1X" --v2 "500 mL" --export stock.xlsx

3) Serial dilution

python -m labcalc.cli serial --ratio 10 --steps 6 --vfinal "1 mL" --export serial.xlsx

4) Molarity from powder

python -m labcalc.cli molarity --mw 121.14 --molarity "1 M" --volume "100 mL" --export tris_1M_100mL.xlsx

5) Percent solutions

w/v:

python -m labcalc.cli percent --kind wv --percent 10 --final-volume "100 mL" --export sds_10wv.xlsx

v/v:

python -m labcalc.cli percent --kind vv --percent 70 --final-volume "500 mL" --export ethanol_70vv_500mL.xlsx

Tests
pytest -q
