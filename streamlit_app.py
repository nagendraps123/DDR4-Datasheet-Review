import streamlit as st
import pandas as pd
import re
from PyPDF2 import PdfReader
from fpdf import FPDF
import base64
from datetime import datetime

# --- 1. GLOBAL DATA (Ensures all variables exist before the app runs) ---
AUDIT_CONTENT = {
    "1. Physical Architecture": {
        "intro": "Validates silicon-to-ball delays and bank group configurations.",
        "df": pd.DataFrame({
            "Feature": ["Density", "Package", "Bank Groups", "Pkg Delay"],
            "Value": ["8Gb (512Mx16)", "96-FBGA", "2 Groups", "75 ps"],
            "Spec": ["Standard", "Standard", "x16 Type", "100ps Max"],
            "Significance": ["Determines total addressable memory space.", "Defines land pattern.", "Critical for interleaving efficiency.", "Silicon-to-ball delay matching."]
        })
    },
    "2. DC Power": {
        "intro": "Audits voltage rail tolerances (VDD, VPP) to prevent bit-flip errors.",
        "df": pd.DataFrame({
            "Feature": ["VDD", "VPP", "VMAX", "IDD6N"],
            "Value": ["1.20V", "2.50V", "1.50V", "22 mA"],
            "Spec": ["1.26V Max", "2.75V Max", "1.50V Max", "30mA Max"],
            "Significance": ["Core logic supply stability.", "Wordline boost voltage.", "Absolute maximum stress limit.", "Battery life / Standby current."]
        })
    }
}

VERDICT = "FULLY QUALIFIED (98%)"
MITIGATIONS = [
    "BIOS: Use 2X Refresh scaling for T-case >85C.",
    "PCB Layout: Apply 75ps Pkg Delay compensation.",
    "Signal: Enable DBI to reduce noise.",
    "Reliability: Enable CRC in EMI-heavy zones."
]

# --- 2. PROFESSIONAL PDF ENGINE ---
class JEDEC_PDF(FPDF):
    def __init__(self, p_name="N/A", p_num="TBD"):
        super().__init__()
        self.p_name = p_name
        self.p_num = p_num

    def header(self):
        self.set_font('Arial', 'B', 15
                      
