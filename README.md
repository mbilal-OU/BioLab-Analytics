# 🧪 Bio Lab Calculator

**Author:** MBILAL  
**Affiliation:** Oakland University  
**Version:** v0.1.0 (Phase 1 – Liquids)  
**License:** MIT  

Bio Lab Calculator is a free, open-source Python toolkit designed for **biology students and teaching laboratories** to perform **common wet-lab calculations accurately, reproducibly, and safely**.

The core idea of this project is:

> **Students provide inputs → the tool returns correct values + Excel outputs**

This reduces calculation errors, improves reproducibility, and supports learning through transparent formulas.

---

## ✨ Features (Phase 1 – Liquids)

- Single dilution (**C1V1 = C2V2**)
- Stock → working solution (e.g. **10X → 1X**)
- Serial dilution tables
- Molarity calculation from powder (MW-based)
- Percent solutions (**w/v** and **v/v**)
- Automatic Excel export
- Unit validation and pipetting warnings
- Fully tested with `pytest`

---

## 📁 Project Structure

lab_calculator/
├── labcalc/
│ ├── init.py
│ └── cli.py
├── tests/
│ └── test_liquids.py
├── examples/
│ ├── dilution_demo.xlsx
│ ├── molarity_demo.xlsx
│ └── ethanol_70_demo.xlsx
├── README.md
├── requirements.txt
├── pytest.ini
└── LICENSE


---

## 🚀 Installation

Clone the repository and set up a virtual environment:

```bash
git clone https://github.com/mbilal-OU/lab_calculator.git
cd lab_calculator

python -m venv .venv
# Linux / WSL / macOS
source .venv/bin/activate
# Windows PowerShell
# .\.venv\Scripts\Activate.ps1

pip install -r requirements.txt

🧮 Usage (Command Line Interface)

1️⃣ Single dilution (C1V1 = C2V2)
python -m labcalc.cli dilute \
  --c1 "10 mM" \
  --c2 "1 mM" \
  --v2 "50 mL" \
  --export dilution.xlsx
2️⃣ Stock-to-working solution (10X → 1X)
python -m labcalc.cli stock-to-working \
  --stock "10X" \
  --final "1X" \
  --v2 "500 mL" \
  --export stock.xlsx
3️⃣ Serial dilution
python -m labcalc.cli serial \
  --ratio 10 \
  --steps 6 \
  --vfinal "1 mL" \
  --export serial.xlsx
4️⃣ Molarity from powder (MW-based)
python -m labcalc.cli molarity \
  --mw 121.14 \
  --molarity "1 M" \
  --volume "100 mL" \
  --export tris_1M_100mL.xlsx
Example result:
1 M Tris, 100 mL → 12.114 g

5️⃣ Percent solutions
w/v (e.g. 10% SDS, 100 mL)

python -m labcalc.cli percent \
  --kind wv \
  --percent 10 \
  --final-volume "100 mL" \
  --export sds_10wv.xlsx
python -m labcalc.cli percent \
  --kind wv \
  --percent 10 \
  --final-volume "100 mL" \
  --export sds_10wv.xlsx

v/v (e.g. 70% ethanol, 500 mL)
python -m labcalc.cli percent \
  --kind vv \
  --percent 70 \
  --final-volume "500 mL" \
  --export ethanol_70vv_500mL.xlsx
Expected result:
70% v/v of 500 mL → 350 mL ethanol + 150 mL water

🧪 Tests

All calculations are validated using automated tests.

Run the test suite:
pytest -q
Expected output:
5 passed in <1s

🎓 Educational Value

This project is designed to:

Reduce calculation errors in wet labs

Teach dimensional analysis and unit handling

Demonstrate real-world Python for biology

Serve as a reusable departmental tool

