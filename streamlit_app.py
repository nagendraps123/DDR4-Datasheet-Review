import streamlit as st
import pandas as pd
from fpdf import FPDF
from datetime import datetime
import re
from PyPDF2 import PdfReader

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

# --- PDF Extraction ---
def extract_ddr4_params(uploaded_file):
    reader = PdfReader(uploaded_file)
    text = ""
    for page in reader.pages:
        if page.extract_text():
            text += page.extract_text()

    params = {}
    patterns = {
        "Density": r"(\d+Gb|\d+Mb).*x\d+",
        "Package": r"(FBGA|BGA|CSP).*",
        "Bank Groups": r"Bank Groups.*?(\d+)",
        "VDD": r"VDD.*?(\d\.\d+V)",
        "VPP": r"VPP.*?(\d\.\d+V)",
        "Absolute Max VDD": r"Absolute Max.*?(\d\.\d+V)",
        "IDD6N": r"IDD6N.*?(\d+ mA)",
        "tCK": r"tCK.*?(\d+\.\d+ ns)",
        "tCL": r"CL.*?(\d+ cycles)",
        "tRCD": r"tRCD.*?(\d+ cycles)",
        "tRP": r"tRP.*?(\d+ cycles)",
        "tRAS": r"tRAS.*?(\d+ ns)",
        "tFAW": r"tFAW.*?(\d+ ns)",
        "Toper": r"Operating Temperature.*?(\d+ ?to ?\d+ ?°C)",
        "Tstorage": r"Storage Temperature.*?(\-?\d+ ?to ?\d+ ?°C)",
        "tREFI": r"tREFI.*?(\d+\.\d+ µs)",
        "CA Parity": r"CA Parity.*?(Enabled|Disabled)",
        "CRC": r"CRC.*?(Enabled|Disabled)",
        "DBI": r"DBI.*?(Enabled|Disabled)",
        "ACT_n": r"ACT_n.*?(Supported|Not Supported)"
    }

    for key, pattern in patterns.items():
        m = re.search(pattern, text, re.IGNORECASE)
        params[key] = m.group(1) if m else "Not Found"

    return params

# --- STREAMLIT APP ---
st.title("DDR4 Datasheet Compliance Audit Tool")

st.markdown("""
This tool helps engineers and managers review DDR4 datasheets against
JEDEC JESD79-4 specifications.

**Workflow:**
1. Upload the vendor's DDR4 datasheet (PDF).
2. The tool extracts key parameters automatically.
3. Each section is cross-checked against JEDEC limits.
4. A verdict (PASS/FAIL) is generated with JEDEC references.
5. Download a professional PDF report with embedded JEDEC link.

Reference: [JEDEC DDR4 Standard JESD79-4](https://www.jedec.org/standards-documents/docs/jesd79-4)
""")

uploaded_file = st.file_uploader("Upload DDR4 Datasheet (PDF)", type=["pdf"])
part_number = st.text_input("Enter Part Number:", "Unknown-Part")

if uploaded_file:
    extracted = extract_ddr4_params(uploaded_file)

    # Build dynamic audit sections
    AUDIT_SECTIONS = {
        "1. Physical Architecture": {
            "intro": "Validates silicon-to-package interface.",
            "df": pd.DataFrame({
                "Feature": ["Density", "Package", "Bank Groups"],
                "Value": [extracted["Density"], extracted["Package"], extracted["Bank Groups"]],
                "Spec": ["JEDEC JESD79-4 Compliant", "Standard FBGA", "4 Groups (x16 devices)"],
                "Significance": ["Defines address mapping", "Package impacts routing", "Bank group interleaving"]
            })
        },
        "2. DC Power": {
            "intro": "Analyzes electrical rails.",
            "df": pd.DataFrame({
                "Feature": ["VDD", "VPP", "Absolute Max VDD", "IDD6N"],
                "Value": [extracted["VDD"], extracted["VPP"], extracted["Absolute Max VDD"], extracted["IDD6N"]],
                "Spec": ["1.14V - 1.26V", "2.375V - 2.625V", "1.50V Max", "30mA Max"],
                "Significance": ["Core supply", "Wordline boost", "Absolute max rating", "Self-refresh current"]
            })
        },
        "3. Timing Parameters": {
            "intro": "Critical AC timing audit.",
            "df": pd.DataFrame({
                "Feature": ["tCK", "tCL", "tRCD", "tRP", "tRAS", "tFAW"],
                "Value": [extracted["tCK"], extracted["tCL"], extracted["tRCD"], extracted["tRP"], extracted["tRAS"], extracted["tFAW"]],
                "Spec": ["0.937ns Min", "CL=16", "tRCD=16", "tRP=16", "≥35 ns", "30 ns"],
                "Significance": ["Clock period", "CAS latency", "RAS-CAS delay", "Precharge", "Row active time", "Four-bank activation window"]
            })
        },
        "4. Thermal & Environmental": {
            "intro": "Evaluates operating/storage ranges and refresh scaling.",
            "df": pd.DataFrame({
                "Feature": ["T-Oper", "T-Storage", "tREFI"],
                "Value": [extracted["Toper"], extracted["Tstorage"], extracted["tREFI"]],
                "Spec": ["0-95°C", "-55-125°C", "7.8µs / 3.9µs"],
                "Significance": ["Operating range", "Storage range", "Refresh interval"]
            })
        },
        "5. Command & Address": {
            "intro": "Verifies CA parity, CRC,
