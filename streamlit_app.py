import streamlit as st
import pandas as pd
from PyPDF2 import PdfReader
from fpdf import FPDF
from datetime import datetime

# --- 1. PDF CLASS WITH HEADER/FOOTER ---
class DRAM_Report(FPDF):
    def __init__(self, part_number):
        super().__init__()
        self.part_number = part_number

    def header(self):
        self.set_font("Arial", 'B', 10)
        self.cell(0, 10, f"DDR Audit Report | Part: {self.part_number}", 0, 1, 'R')
        self.line(10, 18, 200, 18)

    def footer(self):
        self.set_y(-15)
        self.set_font("Arial", 'I', 8)
        self.cell(0, 10, f"Page {self.page_no()} | Part Number: {self.part_number}", 0, 0, 'C')

# --- 2. GLOBAL AUDIT CONTENT (Fixed Syntax) ---
AUDIT_SECTIONS = {
    "1. Physical Architecture": {
        "intro": "Validates silicon-to-ball delays and bank group configurations to ensure signal integrity.",
        "df": pd.DataFrame({
            "Feature": ["Density", "Package", "Bank Groups", "Pkg Delay"],
            "Value": ["8Gb (512Mx16)", "96-FBGA", "2 Groups", "75 ps"],
            "Spec": ["Standard", "Standard", "x16 Type", "100ps Max"],
            "Significance": ["Addressable memory space.", "Physical land pattern.", "Interleaving efficiency.", "Internal delay offset."]
        })
    },
    "2. DC Power": {
        "intro": "Audits voltage rail tolerances (VDD, VPP) to prevent bit-flips and lattice stress.",
        "df": pd.DataFrame({
            "Feature": ["VDD", "VPP", "VMAX", "IDD6N"],
            "Value": ["1.20V", "2.50V", "1.50V", "22 mA"],
            "Spec": ["1.26V Max", "2.75V Max", "1.50V Max", "30mA Max"],
            "Significance": ["Core stability; ripple >5% causes errors.", "Wordline boost requirements.", "Max safety rating.", "Self-refresh current draw."]
        })
    },
    "3. Timing Parameters": {
        "intro": "Analyzes critical clock cycles (tCK) and data strobe latencies (tCL, tRCD, tRP).",
        "df": pd.DataFrame({
            "Feature": ["tCK (avg)", "tCL", "tRCD", "tRP"],
            "Value": ["0.938 ns", "16 cycles", "16 cycles", "16 cycles"],
            "Spec": ["0.937ns Min", "CL=16", "tRCD=16", "tRP=16"],
            "Significance": ["Main clock frequency.", "Read CAS latency.", "RAS to CAS delay.", "Row precharge timing."]
        })
    },
    "4. Thermal & Environmental": {
        "intro": "Reviews operating temperature ranges and refresh rate scaling based on heat levels.",
        "df": pd.DataFrame({
            "Feature": ["T-Oper", "T-Storage", "Refresh Rate", "Thermal Sensor"],
            "Value": ["0°C to 95°C", "-55°C to 100°C", "64ms @ <85°C", "Integrated"],
            "Spec": ["Standard", "Standard", "32ms @ >85°C", "JEDEC Compliant"],
            "Significance": ["Safe operating window.", "Long-term storage limit.", "Data integrity vs heat.", "Thermal monitoring."]
        })
    },
    "5. Command & Address": {
        "intro": "Evaluates command bus signaling, parity checking, and error retry capabilities.",
        "df": pd.DataFrame({
            "Feature": ["C/A Latency", "CA Parity", "CRC Error", "DBI"],
            "Value": ["Disabled", "Enabled", "Auto-Retry", "Enabled"],
            "Spec": ["Optional", "Required", "Optional", "x16 Support"],
            "Significance": ["Bus timing offset.", "Detects bus errors.", "Corrects data errors.", "Reduces power/noise via inversion."]
        })
    }
}

# --- 3. UI LAYOUT ---
st.set_page_config(page_title="DRAM Audit Tool", layout="wide")

st.title("🛡️ DRAM Specification & Compliance Audit")

# Main Screen Upload
st.header("1. Datasheet Initialization")
uploaded_file = st.file_uploader("Upload PDF Datasheet to begin", type="pdf")
part_no = st.text_input("Enter DDR Part Number", value="MT40A512M16")

if uploaded_file:
    st.success("✅ Datasheet Uploaded Successfully")
    
    # Sidebar only appears after upload
    st.sidebar.header("Audit Navigation")
    section_choice = st.sidebar.selectbox("Choose Category", list(AUDIT_SECTIONS.keys()))
    
    # Main Content
    content = AUDIT_SECTIONS[section_choice]
    st.markdown("---")
    st.header(f"{section_choice} | {part_no}")
    st.info(f"**Section
    
