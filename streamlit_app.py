import streamlit as st
import pandas as pd
from fpdf import FPDF
from datetime import datetime
import re

# --- PDF CLASS ---
class DRAM_Report(FPDF):
    def __init__(self, part_number, logo_path=None):
        super().__init__()
        self.part_number = part_number
        self.logo_path = logo_path

    def header(self):
        if self.logo_path:
            try:
                self.image(self.logo_path, 10, 8, 20)
            except:
                pass
        self.set_font("Arial", 'B', 10)
        self.cell(0, 10, f"DDR Compliance Audit | Part No: {self.part_number}", 0, 1, 'R')
        self.line(10, 18, 200, 18)

    def footer(self):
        self.set_y(-15)
        self.set_font("Arial", 'I', 8)
        self.cell(0, 10, f"Page {self.page_no()} | Part Number: {self.part_number}", 0, 0, 'C')

# --- COMPLIANCE CHECKING ---
def normalize_value(val):
    try:
        return float(re.findall(r"[\d.]+", val)[0])
    except:
        return None

def check_compliance(value, spec):
    try:
        val = normalize_value(value)
        if "-" in spec:  # range
            low, high = [normalize_value(x) for x in spec.split("-")]
            return val is not None and low <= val <= high
        elif "Max" in spec:
            limit = normalize_value(spec)
            return val is not None and val <= limit
        elif "Min" in spec:
            limit = normalize_value(spec)
            return val is not None and val >= limit
        elif "Required" in spec:
            return value.strip().lower() == "enabled"
        return True
    except:
        return True

def compute_verdict(sections):
    section_results = {}
    issues = []
    for section, content in sections.items():
        df = content["df"]
        section_pass = True
        for _, row in df.iterrows():
            if not check_compliance(str(row["Value"]), str(row["Spec"])):
                section_pass = False
                issues.append(f"{section}: {row['Feature']} ({row['Value']} vs {row['Spec']}) [JEDEC JESD79-4]")
        section_results[section] = "PASS" if section_pass else "FAIL"
    overall = "PASS" if all(r=="PASS" for r in section_results.values()) else "FAIL"
    return overall, section_results, issues

# --- THERMAL REFRESH CALCULATOR ---
def thermal_refresh_calc(temp_c):
    if temp_c <= 85:
        return "tREFI = 7.8 µs (<85°C, JEDEC JESD79-4)"
    elif temp_c <= 95:
        return "tREFI = 3.9 µs (>85°C, JEDEC JESD79-4)"
    else:
        return "Out of JEDEC operating range"

# --- AUDIT DATA (example subset, expand as needed) ---
AUDIT_SECTIONS = {
    "1. Physical Architecture": {
        "intro": "Validates silicon-to-package interface and signal path matching.",
        "df": pd.DataFrame({
            "Feature": ["Density", "Package", "Bank Groups", "tDQSCK"],
            "Value": ["8Gb (512Mx16)", "96-FBGA", "4 Groups", "100 ps"],
            "Spec": ["JESD79-4 Compliant", "Standard", "x16 Type", "≤125 ps"],
            "Significance": ["Address mapping", "Ball pitch/layout", "Bank Group interleaving", "DQS-DQ skew"]
        })
    },
    "2. DC Power": {
        "intro": "Analyzes electrical rails against JEDEC DC specifications.",
        "df": pd.DataFrame({
            "Feature": ["VDD", "VPP", "Absolute Max VDD", "IDD6N"],
            "Value": ["1.20V", "2.50V", "1.50V", "22 mA"],
            "Spec": ["1.14V - 1.26V", "2.375V - 2.625V", "1.50V Max", "30mA Max"],
            "Significance": ["Core supply", "Wordline boost", "Absolute max rating", "Self-refresh current"]
        })
    },
    "3. Timing Parameters": {
        "intro": "Critical AC timing audit per JEDEC speed bin.",
        "df": pd.DataFrame({
            "Feature": ["tCK (avg)", "tCL", "tRCD", "tRP", "tRAS", "tFAW"],
            "Value": ["0.938 ns", "16 cycles", "16 cycles", "16 cycles", "35 ns", "30 ns"],
            "Spec": ["0.937ns Min", "CL=16", "tRCD=16", "tRP=16", "≥35 ns", "30 ns"],
            "Significance": ["Clock period", "CAS latency", "RAS-CAS delay", "Precharge", "Row active time", "Four-bank activation window"]
        })
    },
    "4. Thermal & Environmental": {
        "intro": "Evaluates operating/storage ranges and refresh scaling.",
        "df": pd.DataFrame({
            "Feature": ["T-Oper", "T-Storage", "tREFI (<85°C)", "tREFI (>85°C)"],
            "Value": ["0 to 95 °C", "-55 to 125 °C", "7.8 µs", "3.9 µs"],
            "Spec": ["JEDEC JESD79-4", "JEDEC JESD79-4", "7.8 µs", "3.9 µs"],
            "Significance": ["Operating range", "Storage range", "Nominal refresh", "High-temp refresh"]
        })
    },
    "5. Command & Address": {
        "intro": "Verifies CA parity, CRC, DBI compliance.",
        "df": pd.DataFrame({
            "Feature": ["CA Parity", "CRC (Write)", "DBI", "ACT_n Command"],
            "Value": ["Enabled", "Enabled", "Enabled", "Supported"],
            "Spec": ["Required", "Required", "Optional", "Required"],
            "Significance": ["Error detection", "Data integrity", "Signal integrity", "DDR4-specific command"]
        })
    }
}

# --- STREAMLIT APP ---
st.title("DDR4 Compliance Audit Tool")
st.markdown("### Reference: [JEDEC DDR4 Standard JESD79-4](https://www.jedec.org/standards-documents/docs/jesd79-4)")

part_number = st.text_input("Enter Part Number:", "ABC123")

# Display sections
for section, content in AUDIT_SECTIONS.items():
    with st.expander(section, expanded=True):
        st.write(content["intro"])
        df = content["df"]

        def highlight(row):
            return ['background-color: #ffcccc' if not check_compliance(str(row["Value"]), str(row["Spec"])) else '' for _ in row]

        st.dataframe(df.style.apply(highlight, axis=1))
        st.download_button("Download Section CSV", df.to_csv(index=False), file_name=f"{section.replace(' ','_')}.csv")

# Thermal refresh calculator
temp_input = st.number_input("Enter Operating Temp (°C):", 0, 125, 25)
st.write("Refresh Requirement:", thermal_refresh_calc(temp_input))

# Verdict
overall_verdict, section_results, issues = compute_verdict(AUDIT_SECTIONS)
st.subheader("Final Audit Verdict")
for sec, res in section_results.items():
    st.write(f"{'✔' if res=='PASS' else '❌'} {sec}: {res}")
st.write(f"**Overall Verdict: {overall_verdict}**")
if issues:
    st.write("Issues found:")
    for i in issues:
        st.write(f"- {i}")

# PDF Generation
if st.button("Generate PDF Report"):
    pdf = DRAM_Report(part_number=part_number, logo_path=None)
    pdf.add_page()

    for section, content in AUDIT_SECTIONS.items():
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(0, 10, section, ln=True)
        pdf.set_font("Arial", '', 10)
        pdf.multi_cell(0, 10, content["intro"])
        pdf.ln(2)

        df = content["df"]
        pdf.set_font("Arial", '', 9)
        col_widths = [40, 40, 40, 70]
        headers = ["Feature", "Value", "Spec", "Significance"]

        # Table header
        for i, h in enumerate
