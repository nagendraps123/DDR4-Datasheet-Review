import streamlit as st
import pandas as pd
import re
from PyPDF2 import PdfReader
from fpdf import FPDF
import base64
from datetime import datetime

# --- 1. GLOBAL DATA (Prevents all NameErrors) ---
AUDIT_SECTIONS = {
    "1. Physical Architecture": {
        "intro": "Validates silicon-to-ball delays, bank group configurations, and physical land patterns.",
        "df": pd.DataFrame({
            "Feature": ["Density", "Package", "Bank Groups", "Pkg Delay"],
            "Value": ["8Gb (512Mx16)", "96-FBGA", "2 Groups", "75 ps"],
            "Spec": ["Standard", "Standard", "x16 Type", "100ps Max"],
            "Significance": ["Determines total addressable memory space.", "Defines physical land pattern.", "Critical for interleaving efficiency.", "Internal silicon-to-ball delay offset."]
        })
    },
    "2. DC Power": {
        "intro": "Audits voltage rail tolerances (VDD, VPP) to prevent lattice stress.",
        "df": pd.DataFrame({
            "Feature": ["VDD", "VPP", "VMAX", "IDD6N"],
            "Value": ["1.20V", "2.50V", "1.50V", "22 mA"],
            "Spec": ["1.26V Max", "2.75V Max", "1.50V Max", "30mA Max"],
            "Significance": ["Core stability; ripple >5% causes bit-flips.", "Wordline boost for row activation.", "Absolute stress limit.", "Standby battery life."]
        })
    },
    "3. AC Timing": {
        "intro": "Analyzes signal integrity and clock period margins.",
        "df": pd.DataFrame({
            "Feature": ["tCK", "tAA", "tRFC", "Slew Rate"],
            "Value": ["625 ps", "13.75 ns", "350 ns", "5.0 V/ns"],
            "Spec": ["625ps Min", "13.75ns Max", "350ns Std", "4V/ns Min"],
            "Significance": ["3200 MT/s limit.", "Read Latency delay.", "Refresh cycle window.", "Data Eye sharpness."]
        })
    },
    "4. Thermal Reliability": {
        "intro": "Validates refresh rate scaling for data retention.",
        "df": pd.DataFrame({
            "Feature": ["T-Case Max", "Normal Ref", "Extended Ref", "ASR"],
            "Value": ["95C", "1X (0-85C)", "2X (85-95C)", "Supported"],
            "Spec": ["JEDEC Limit", "7.8us", "3.9us", "Optional"],
            "Significance": ["Maximum operating temperature.", "Standard retention.", "Heat leakage fix.", "Auto power mgmt."]
        })
    },
    "5. Advanced Integrity": {
        "intro": "Audits error detection and signal correction features.",
        "df": pd.DataFrame({
            "Feature": ["CRC", "DBI", "Parity", "PPR"],
            "Value": ["Yes", "Yes", "Yes", "Yes"],
            "Spec": ["Optional", "Optional", "Optional", "Optional"],
            "Significance": ["Bus error detection.", "Noise reduction.", "Ghost cmd prevention.", "Post-Package Repair."]
        })
    }
}

VERDICT_TEXT = "VERDICT: FULLY QUALIFIED (98%)"
MITIGATIONS = [
    "BIOS: Use 2X Refresh scaling for T-case >85C.",
    "PCB Layout: Apply 75ps Pkg Delay compensation.",
    "Signal: Enable DBI to reduce VDDQ switching noise.",
    "Reliability: Enable CRC in high-EMI zones."
]

# --- 2. PDF ENGINE ---
class JEDEC_PDF(FPDF):
    def __init__(self, p_name="N/A", p_num="TBD"):
        super().__init__()
        self.p_name, self.p_num = p_name, p_num
    def header(self):
        self.set_font('Arial', 'B', 15)
        self.cell(0,
        
