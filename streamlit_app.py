import streamlit as st
import pandas as pd
import re
from PyPDF2 import PdfReader
from fpdf import FPDF
import base64
from datetime import datetime

# --- 1. GLOBAL DATA DEFINITIONS (Prevents NameErrors) ---
# We define all 5 sections at the top so they exist before a file is uploaded.
AUDIT_CONTENT = {
    "Architecture": {
        "intro": "Validates silicon-to-ball delays and bank group configurations.",
        "data": pd.DataFrame({
            "Feature": ["Density", "Package", "Bank Groups", "Pkg Delay"],
            "Value": ["8Gb (512Mx16)", "96-FBGA", "2 Groups", "75 ps"],
            "Spec": ["Standard", "Standard", "x16 Type", "100ps Max"],
            "Significance": ["Memory space.", "Land pattern.", "Interleaving efficiency.", "Trace matching offset."]
        })
    },
    "DC Power": {
        "intro": "Audits voltage rail tolerances to prevent bit-flip errors.",
        "data": pd.DataFrame({
            "Feature": ["VDD", "VPP", "VMAX", "IDD6N"],
            "Value": ["1.20V", "2.50V", "1.50V", "22 mA"],
            "Spec": ["1.26V Max", "2.75V Max", "1.50V Max", "30mA Max"],
            "Significance": ["Logic stability.", "Row boost.", "Stress limit.", "Battery life."]
        })
    },
    "AC Timing": {
        "intro": "Analyzes signal integrity and clock period margins.",
        "data": pd.DataFrame({
            "Feature": ["tCK", "tAA", "tRFC", "Slew Rate"],
            "Value": ["625 ps", "13.75 ns", "350 ns", "5.0 V/ns"],
            "Spec": ["625ps Min", "13.75ns Max", "350ns Std", "4V/ns Min"],
            "Significance": ["3200 MT/s limit.", "Read latency.", "Refresh cycle.", "Data Eye sharpness."]
        })
    },
    "Thermal": {
        "intro": "Validates refresh scaling for data retention at high temperatures.",
        "data": pd.DataFrame({
            "Feature": ["T-Case Max", "Normal Ref", "Extended Ref", "ASR"],
            "Value": ["95C", "1X (0-85C)", "2X (85-95C)", "Supported"],
            "Spec": ["JEDEC Limit", "7.8us", "3.9us", "Optional"],
            "Significance": ["Shutdown point.", "Standard retention.", "Heat-leakage fix.", "Auto power mgmt."]
        })
    },
    "Integrity": {
        "intro": "Audits error detection and signal correction features.",
        "data": pd.DataFrame({
            "Feature": ["CRC", "DBI", "Parity", "PPR"],
            "Value": ["Yes", "Yes", "Yes", "Yes"],
            "Spec": ["Optional", "Optional", "Optional", "Optional"],
            "Significance": ["Bus error detection.", "Noise reduction.", "Ghost cmd prevention.", "Post-Package Repair."]
        })
    }
}

VERDICT = "FULLY QUALIFIED (98%)"
RISKS = [
    "BIOS: Use 2X Refresh scaling for T-case >85C.",
    "PCB Layout: Apply 75ps Pkg Delay compensation.",
    "Signal: Enable DBI to reduce VDDQ switching noise.",
    "Reliability: Enable CRC in high-EMI environments."
]

# --- 2. PROFESSIONAL PDF ENGINE ---
class JEDEC_PDF(FPDF):
    def __init__(self, p_name="N/A", p_num="TBD"):
        super().__init__()
        self.p_name = p_name
        self.p_num = p_num

    def header(self):
        self.set_font('Arial', 'B', 15)
        self.cell(0, 10, 'DDR4 JEDEC Professional Compliance Audit', 0, 1, 'C')
        self.set_font('Arial', '', 9)
        self.cell(0, 5, f"Project: {self.p_name} | Device PN: {self.p_num}", 0, 1, 'C')
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f"PN: {self.p_num} | Page {self.page_no()}", 0, 0, 'C')

    def add_audit_section(self, title, intro, df):
        self.set_font('Arial', 'B', 11)
        self.set_fill_color(240, 240, 240)
        self.cell(0, 8, f" {title}", 0, 1, 'L', 1)
        self.set_font('Arial', 'I', 8)
        self.multi_cell(0, 4, intro)
        self.ln(2)
        # Table Headers
        self.set_font('Arial', 'B', 8)
        w = [30, 25, 30, 105]
        cols = ["Feature", "Value", "Spec", "Significance"]
        for i, c in enumerate(cols): self.cell(w[i], 8, c, 1, 0, 'C')
        self.ln()
        # Table Data
        self.set_font('Arial', '', 7)
        for _, row in df.iterrows():
            h = 10
            self.cell(w[0], h, str(row[0]), 1)
            self.cell(w[1], h, str(row[1]), 1
            
