import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))


import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

from biolab_analytics.calculators.solution_chemistry import (
    mass_for_molar_solution, molarity_from_mass, percent_wv_mass, percent_vv_volume
)
from biolab_analytics.calculators.dilution import c1v1, serial_dilution
from biolab_analytics.calculators.microbiology import cfu_per_ml, growth_rate, doubling_time
from biolab_analytics.calculators.molecular_biology import dna_copy_number, pcr_mastermix
from biolab_analytics.calculators.cell_culture import (
    cell_seeding_volume, viability_percent, population_doubling_time
)
from biolab_analytics.calculators.sequencing import genome_coverage, reads_required

st.set_page_config(page_title="BioLab Analytics", page_icon="🧪", layout="wide")

CUSTOM_CSS = """
<style>
.main-title {
    font-size: 3rem;
    font-weight: 800;
    margin-bottom: 0rem;
}
.subtitle {
    font-size: 1.25rem;
    color: #4b5563;
    margin-bottom: 1.5rem;
}
.card {
    padding: 1.2rem;
    border-radius: 18px;
    background: linear-gradient(135deg, #f8fafc 0%, #eef2ff 100%);
    border: 1px solid #e5e7eb;
    box-shadow: 0 2px 8px rgba(15, 23, 42, 0.06);
    min-height: 150px;
}
.card-title {
    font-size: 1.25rem;
    font-weight: 700;
}
.card-text {
    color: #4b5563;
    font-size: 0.95rem;
}
.result-box {
    padding: 1rem;
    border-radius: 12px;
    background-color: #ecfdf5;
    border: 1px solid #10b981;
    font-size: 1.1rem;
}
.formula-box {
    padding: 1rem;
    border-radius: 12px;
    background-color: #f8fafc;
    border-left: 5px solid #2563eb;
}
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

if "history" not in st.session_state:
    st.session_state.history = []

def add_history(calculator, result):
    st.session_state.history.append({"calculator": calculator, "result": result})

def download_table(df, filename):
    return st.download_button(
        "Download results as CSV",
        data=df.to_csv(index=False).encode("utf-8"),
        file_name=filename,
        mime="text/csv",
    )

def formula_panel(formula, explanation):
    st.markdown(f"""
    <div class="formula-box">
    <b>Formula</b><br>
    <code>{formula}</code><br><br>
    <b>Interpretation</b><br>
    {explanation}
    </div>
    """, unsafe_allow_html=True)

with st.sidebar:
    st.markdown("## 🧪 BioLab Analytics")
    module = st.radio(
        "Choose workspace",
        [
            "🏠 Home",
            "🧪 Prepare Solutions",
            "🧫 Dilutions",
            "🦠 Microbiology",
            "🧬 Molecular Biology",
            "🔬 Cell Culture",
            "💻 Sequencing",
            "📜 Calculation History",
        ],
    )

if module == "🏠 Home":
    st.markdown('<div class="main-title">🧪 BioLab Analytics</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitle">Interactive quantitative biosciences workspace for laboratory calculations, experimental planning, and reproducible research workflows.</div>', unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    col1.metric("Workspaces", "6")
    col2.metric("Calculators", "15+")
    col3.metric("Access", "Dashboard + CLI")

    st.markdown("## Start from a workflow")
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown('<div class="card"><div class="card-title">🧪 Prepare Solutions</div><div class="card-text">Molarity, mass, %w/v, %v/v, and stock preparation.</div></div>', unsafe_allow_html=True)
    with c2:
        st.markdown('<div class="card"><div class="card-title">🦠 Culture Microbes</div><div class="card-text">CFU/mL, serial dilution planning, growth rate, and doubling time.</div></div>', unsafe_allow_html=True)
    with c3:
        st.markdown('<div class="card"><div class="card-title">🧬 Run Molecular Biology</div><div class="card-text">DNA copy number and PCR mastermix planning.</div></div>', unsafe_allow_html=True)

    c4, c5, c6 = st.columns(3)
    with c4:
        st.markdown('<div class="card"><div class="card-title">🔬 Plan Cell Culture</div><div class="card-text">Cell seeding, viability, and population doubling time.</div></div>', unsafe_allow_html=True)
    with c5:
        st.markdown('<div class="card"><div class="card-title">💻 Plan Sequencing</div><div class="card-text">Genome coverage and read requirement estimation.</div></div>', unsafe_allow_html=True)
    with c6:
        st.markdown('<div class="card"><div class="card-title">📊 Reuse Results</div><div class="card-text">Download calculation tables and track session history.</div></div>', unsafe_allow_html=True)

    st.markdown("## Most used calculators")
    q1, q2, q3, q4, q5 = st.columns(5)
    q1.info("Molarity")
    q2.info("Dilution")
    q3.info("CFU/mL")
    q4.info("PCR mix")
    q5.info("Coverage")

elif module == "🧪 Prepare Solutions":
    st.header("🧪 Prepare Solutions")
    tab1, tab2, tab3, tab4 = st.tabs(["Molar solution", "Molarity from mass", "% w/v", "% v/v"])

    with tab1:
        formula_panel("mass (g) = molarity × volume × molecular weight", "Use this for preparing molar stock solutions such as NaCl, Tris, or antibiotics.")
        c1, c2, c3 = st.columns(3)
        molarity = c1.number_input("Target molarity (M)", min_value=0.0, value=1.0, step=0.1)
        volume = c2.number_input("Final volume (L)", min_value=0.0, value=1.0, step=0.1)
        mw = c3.number_input("Molecular weight (g/mol)", min_value=0.0, value=58.44, step=0.01)
        if st.button("Calculate mass", key="mass_button"):
            mass = mass_for_molar_solution(molarity, volume, mw)
            st.success(f"Mass required: {mass:.4f} g")
            add_history("Molar solution", f"{mass:.4f} g")
            df = pd.DataFrame([{"molarity_M": molarity, "volume_L": volume, "molecular_weight": mw, "mass_g": mass}])
            download_table(df, "molar_solution_result.csv")

    with tab2:
        formula_panel("M = mass / (molecular weight × volume)", "Use this to calculate actual molarity when a known mass is dissolved to a known volume.")
        c1, c2, c3 = st.columns(3)
        mass = c1.number_input("Mass (g)", min_value=0.0, value=58.44)
        volume = c2.number_input("Volume (L)", min_value=0.0, value=1.0, key="mfm_volume")
        mw = c3.number_input("Molecular weight (g/mol)", min_value=0.0, value=58.44, key="mfm_mw")
        if st.button("Calculate molarity", key="molarity_button"):
            result = molarity_from_mass(mass, volume, mw)
            st.success(f"Molarity: {result:.4f} M")
            add_history("Molarity from mass", f"{result:.4f} M")

    with tab3:
        formula_panel("mass (g) = (% w/v × final volume mL) / 100", "A 1% w/v solution contains 1 g solute per 100 mL final solution.")
        percent = st.number_input("% w/v", min_value=0.0, value=1.0)
        vol_ml = st.number_input("Final volume (mL)", min_value=0.0, value=100.0)
        if st.button("Calculate w/v mass"):
            mass = percent_wv_mass(percent, vol_ml)
            st.success(f"Mass required: {mass:.4f} g")
            add_history("% w/v", f"{mass:.4f} g")

    with tab4:
        formula_panel("solute volume = (% v/v × final volume mL) / 100", "A 70% v/v ethanol solution contains 70 mL ethanol per 100 mL final solution.")
        percent = st.number_input("% v/v", min_value=0.0, value=70.0)
        vol_ml = st.number_input("Final volume (mL)", min_value=0.0, value=100.0, key="vv_vol")
        if st.button("Calculate v/v volume"):
            solute = percent_vv_volume(percent, vol_ml)
            st.success(f"Solute volume: {solute:.4f} mL")
            st.info(f"Diluent volume: {vol_ml - solute:.4f} mL")
            add_history("% v/v", f"{solute:.4f} mL solute")

elif module == "🧫 Dilutions":
    st.header("🧫 Dilutions")
    tab1, tab2 = st.tabs(["C1V1 = C2V2", "Serial dilution planner"])

    with tab1:
        formula_panel("C1V1 = C2V2", "Use this to dilute a concentrated stock into a lower final concentration.")
        c1v = st.number_input("Stock concentration (C1)", min_value=0.0, value=100.0)
        c2v = st.number_input("Final concentration (C2)", min_value=0.0, value=1.0)
        v2 = st.number_input("Final volume (V2)", min_value=0.0, value=100.0)
        if st.button("Calculate dilution"):
            stock, diluent = c1v1(c1v, c2v, v2)
            st.success(f"Stock volume: {stock:.4f}")
            st.info(f"Diluent volume: {diluent:.4f}")
            add_history("Dilution", f"{stock:.4f} stock + {diluent:.4f} diluent")
            df = pd.DataFrame([{"C1": c1v, "C2": c2v, "V2": v2, "stock_volume": stock, "diluent_volume": diluent}])
            download_table(df, "dilution_result.csv")

    with tab2:
        formula_panel("C_n = C_0 / dilution_factor^n", "Generate concentration values across a dilution series.")
        start = st.number_input("Starting concentration", min_value=0.0, value=1e8, format="%.3e")
        factor = st.number_input("Dilution factor", min_value=1.1, value=10.0)
        steps = st.number_input("Number of steps", min_value=1, max_value=20, value=6)
        df = pd.DataFrame(serial_dilution(start, factor, int(steps)))
        st.dataframe(df, use_container_width=True)
        download_table(df, "serial_dilution_table.csv")

        fig, ax = plt.subplots()
        ax.plot(df["step"], df["concentration"], marker="o")
        ax.set_yscale("log")
        ax.set_xlabel("Dilution step")
        ax.set_ylabel("Concentration")
        ax.set_title("Serial dilution profile")
        st.pyplot(fig)

elif module == "🦠 Microbiology":
    st.header("🦠 Microbiology")
    tab1, tab2 = st.tabs(["CFU/mL", "Growth rate and doubling time"])

    with tab1:
        formula_panel("CFU/mL = colonies / (dilution × plated volume)", "Use countable plates and consistent plating volume for reliable viable-cell estimates.")
        colonies = st.number_input("Colonies counted", min_value=0.0, value=120.0)
        dilution = st.number_input("Dilution fraction", min_value=0.0, value=1e-6, format="%.1e")
        volume = st.number_input("Plated volume (mL)", min_value=0.0, value=0.1)
        if st.button("Calculate CFU/mL"):
            value = cfu_per_ml(colonies, dilution, volume)
            st.success(f"CFU/mL: {value:.3e}")
            add_history("CFU/mL", f"{value:.3e}")

    with tab2:
        formula_panel("μ = ln(OD_final / OD_initial) / time; doubling time = ln(2)/μ", "Estimate exponential growth rate from OD measurements.")
        od0 = st.number_input("Initial OD", min_value=0.0, value=0.05)
        od1 = st.number_input("Final OD", min_value=0.0, value=0.8)
        hours = st.number_input("Time (hours)", min_value=0.0, value=4.0)
        if st.button("Calculate microbial growth"):
            mu = growth_rate(od0, od1, hours)
            dt = doubling_time(mu)
            st.success(f"Growth rate: {mu:.4f} h⁻¹")
            st.info(f"Doubling time: {dt:.2f} hours")
            add_history("Growth rate", f"μ={mu:.4f} h⁻¹, DT={dt:.2f} h")

elif module == "🧬 Molecular Biology":
    st.header("🧬 Molecular Biology")
    tab1, tab2 = st.tabs(["DNA copy number", "PCR mastermix"])

    with tab1:
        formula_panel("copies = (mass_g / (length_bp × 660)) × Avogadro", "Estimate DNA molecule copies from DNA mass and sequence length.")
        mass = st.number_input("DNA mass (ng)", min_value=0.0, value=10.0)
        length = st.number_input("Genome/amplicon length (bp)", min_value=0.0, value=5_000_000.0)
        if st.button("Calculate copies"):
            copies = dna_copy_number(mass, length)
            st.success(f"Estimated copies: {copies:.3e}")
            add_history("DNA copy number", f"{copies:.3e}")

    with tab2:
        formula_panel("total volume = per-reaction volume × reactions × extra factor", "Plan PCR mastermix volumes and include extra volume to reduce pipetting loss.")
        reactions = st.number_input("Number of reactions", min_value=1, value=24)
        extra = st.number_input("Extra volume (%)", min_value=0.0, value=10.0)
        st.markdown("Volumes per reaction in µL")
        components = {
            "Water": st.number_input("Water", min_value=0.0, value=17.5),
            "Buffer": st.number_input("Buffer", min_value=0.0, value=2.5),
            "dNTPs": st.number_input("dNTPs", min_value=0.0, value=0.5),
            "Forward primer": st.number_input("Forward primer", min_value=0.0, value=1.0),
            "Reverse primer": st.number_input("Reverse primer", min_value=0.0, value=1.0),
            "Polymerase": st.number_input("Polymerase", min_value=0.0, value=0.5),
            "Template DNA": st.number_input("Template DNA", min_value=0.0, value=2.0),
        }
        result = pd.DataFrame(pcr_mastermix(reactions, extra, components))
        st.dataframe(result, use_container_width=True)
        download_table(result, "pcr_mastermix.csv")

elif module == "🔬 Cell Culture":
    st.header("🔬 Cell Culture")
    tab1, tab2, tab3 = st.tabs(["Cell seeding", "Viability", "Population doubling"])

    with tab1:
        formula_panel("volume μL = target cells / cell density × 1000", "Calculate how much cell suspension is needed to seed a desired number of cells.")
        target = st.number_input("Target cells", min_value=0.0, value=100000.0)
        density = st.number_input("Cell density (cells/mL)", min_value=0.0, value=1e6, format="%.3e")
        if st.button("Calculate seeding volume"):
            vol = cell_seeding_volume(target, density)
            st.success(f"Volume required: {vol:.2f} µL")
            add_history("Cell seeding", f"{vol:.2f} µL")

    with tab2:
        formula_panel("viability (%) = live / (live + dead) × 100", "Estimate cell viability from live/dead counts.")
        live = st.number_input("Live cells", min_value=0.0, value=95.0)
        dead = st.number_input("Dead cells", min_value=0.0, value=5.0)
        if st.button("Calculate viability"):
            viability = viability_percent(live, dead)
            st.success(f"Viability: {viability:.2f}%")
            add_history("Viability", f"{viability:.2f}%")

    with tab3:
        formula_panel("PDT = time × ln(2) / ln(final / initial)", "Estimate population doubling time from cell counts.")
        time = st.number_input("Time (hours)", min_value=0.0, value=24.0)
        initial = st.number_input("Initial cells", min_value=0.0, value=100000.0)
        final = st.number_input("Final cells", min_value=0.0, value=800000.0)
        if st.button("Calculate population doubling time"):
            pdt = population_doubling_time(time, initial, final)
            st.success(f"PDT: {pdt:.2f} hours")
            add_history("Population doubling time", f"{pdt:.2f} hours")

elif module == "💻 Sequencing":
    st.header("💻 Sequencing")
    tab1, tab2 = st.tabs(["Coverage", "Reads required"])

    with tab1:
        formula_panel("coverage = reads × read length / genome size", "Estimate sequencing depth for genome sequencing or assembly planning.")
        reads = st.number_input("Read count", min_value=0.0, value=1_000_000.0, format="%.3e")
        read_len = st.number_input("Read length (bp)", min_value=0.0, value=150.0)
        genome = st.number_input("Genome size (bp)", min_value=0.0, value=5_000_000.0, format="%.3e")
        if st.button("Calculate coverage"):
            cov = genome_coverage(reads, read_len, genome)
            st.success(f"Coverage: {cov:.2f}×")
            add_history("Genome coverage", f"{cov:.2f}×")

    with tab2:
        formula_panel("reads = target coverage × genome size / read length", "Estimate number of reads needed for target coverage.")
        cov = st.number_input("Target coverage", min_value=0.0, value=100.0)
        read_len = st.number_input("Read length (bp)", min_value=0.0, value=150.0, key="req_len")
        genome = st.number_input("Genome size (bp)", min_value=0.0, value=5_000_000.0, format="%.3e", key="req_genome")
        if st.button("Calculate reads required"):
            reads_needed = reads_required(cov, read_len, genome)
            st.success(f"Reads required: {reads_needed:,.0f}")
            add_history("Reads required", f"{reads_needed:,.0f}")

elif module == "📜 Calculation History":
    st.header("📜 Calculation History")
    if st.session_state.history:
        df = pd.DataFrame(st.session_state.history)
        st.dataframe(df, use_container_width=True)
        download_table(df, "biolab_analytics_history.csv")
    else:
        st.info("No calculations recorded in this session yet.")
