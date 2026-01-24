 ## Installation

Clone the repository and set up a virtual environment:

```bash
git clone https://github.com/mbilal-OU/lab_calculator.git
cd lab_calculator

python -m venv .venv
# Linux/WSL/Mac:
source .venv/bin/activate
# Windows PowerShell:
# .\.venv\Scripts\Activate.ps1

pip install -r requirements.txt

Usage (CLI)
1) Single dilution (C1V1 = C2V2)
python -m labcalc.cli dilute --c1 "10 mM" --c2 "1 mM" --v2 "50 mL" --export dilution.xlsx
