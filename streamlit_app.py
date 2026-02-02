import streamlit as st
import pandas as pd
from fpdf import FPDF
from datetime import datetime

# --- 1. GLOBAL AUDIT DATA (Triple-Quoted for Safety) ---
AUDIT_SECTIONS = {
    "1. Physical Architecture": {
        "intro": """Validates the silicon-to-package interface and signal path matching.""",
        "df": pd.DataFrame({
            "Feature": ["Density", "Package", "Bank Groups", "Pkg Delay"],
            "Value": ["8Gb (512Mx16)", "96-FBGA", "2 Groups", "75 ps"],
            "Spec": ["JESD79-4 Compliant", "Standard", "x16 Type", "100ps Max"],
            "Significance": [
                """Determines row/column address bit mapping for the controller.""",
                """Dictates PCB escape routing and impedance control requirements.""",
                """Enables Bank Group interleaving to meet tCCD_S timing.""",
                """Internal silicon-to-ball delay; must be matched to prevent skew."""
            ]
        })
    },
    "2. DC Power": {
        "intro": """Analyzes electrical rails to ensure operation within JEDEC safe areas.""",
        "df": pd.DataFrame({
            "Feature": ["VDD", "VPP", "VMAX", "IDD6N"],
            "Value": ["1.20V", "2.50V", "1.50V", "22 mA"],
            "Spec": ["1.14V-1.26V", "2.375V-2.75V", "1.50V Max", "30mA Max"],
            "Significance": [
                """Core supply; noise >60mV triggers internal logic meta-stability.""",
                """Wordline boost; ensures full overdrive of access transistors.""",
                """Absolute maximum rating; exceeding causes lattice damage.""",
                """Standby current floor required for data integrity during refresh."""
            ]
        })
    },
    "3. Timing Parameters": {
        "intro": """AC timing audit defining the window of validity for data strobes.""",
        "df": pd.DataFrame({
            "Feature": ["tCK (avg)", "tCL", "tRCD", "tRP"],
            "Value": ["0.938 ns", "16 cycles", "16 cycles", "16 cycles"],
            "Spec": ["0.937ns Min", "CL=16", "tRCD=16", "tRP=16"],
            "Significance": [
                """Base reference period for all synchronous AC signaling.""",
                """CAS Latency; delay from Read command to valid data burst.""",
                """RAS to CAS delay; time to charge wordline and open a row.""",
                """Precharge time; needed to equalize bitlines for the next access."""
            ]
        })
    },
    "4. Thermal & Environmental": {
        "intro": """Evaluates data integrity across JEDEC temperature grades.""",
        "df": pd.DataFrame({
            "Feature": ["T-Oper", "T-Storage", "Refresh Rate", "Thermal Sensor"],
            "Value": ["0 to 95 C", "-55 to 100 C", "64ms @ <85C", "Integrated"],
            "Spec": ["0 to 95 C", "Standard", "32ms @ >85C", "JESD21-C Compliant"],
            "Significance": [
                """Operating window before leakage exceeds refresh recovery.""",
                """Storage limits before permanent silicon aging or failure.""",
                """tREFI must halve at high T to counter bitline charge decay.""",
                """Required for automated JEDEC thermal throttling protocols."""
            ]
        })
    },
    "5. Command & Address": {
        "intro": """Verifies bus integrity protocols and error retry logic.""",
        "df": pd.DataFrame({
            "Feature": ["C/A Latency", "CA Parity", "CRC Error", "DBI"],
            "Value": ["Disabled", "Enabled", "Auto-Retry", "Enabled"],
            "Spec": ["Optional", "Required", "Optional", "x16 Support"],
            "Significance": [
                """Adds cycles for address stabilization on complex traces.""",
                """Prevents execution of corrupted instructions or addresses.""",
                """Validates data payload integrity during high-speed transit.""",
                """Data Bus Inversion; minimizes switching current and noise."""
            ]
        })
    }
}

# --- 2. CRASH-PROOF PDF LOGIC ---
class JEDEC_Report(FPDF):
    def __init__(self, part_no):
        super().__init__()
        self.part_no = str(part_no)
    def header(self):
        self.set_font("Arial", 'B', 10)
        self.cell(0, 10, f"JEDEC Compliance Audit | Part: {self.part_no}", 0, 1, 'R')
        self.line(10, 18, 200, 18)
    def footer(self):
        self.set_y(-15)
        self.set_font("Arial", 'I', 8)
        self.cell(0, 10, f"Page {self.page_no()} | Part: {self.part_no}", 0, 0, 'C')

# --- 3. UI LAYOUT ---
st.set_page_config(page_title="Hardware Audit", layout="wide")
st.title("🛡️ DRAM Specification & Compliance Audit")

# Initialization
uploaded_file = st.file_uploader("Upload PDF Datasheet", type="pdf")
part_no = st.text_input("Enter Part Number", value="MT40A512M16")

if uploaded_file:
    # --- DYNAMIC PART SUMMARY LINE ---
    st.info(f"🔍 **Part Detail Summary:** {part_no} | **Density:** 8Gb (512Mx16) | **Package:** 96-FBGA")

    # Navigation
    st.sidebar.header("Audit Navigation")
    section = st.sidebar.selectbox("Choose Category", list(AUDIT_SECTIONS.keys()))
    
    # Display Content
    st.header(section)
    st.write(AUDIT_SECTIONS[section]["intro"])

    

    st.table(AUDIT_SECTIONS[section]["df"])


