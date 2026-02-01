import streamlit as st
import pandas as pd
import re
from PyPDF2 import PdfReader
from fpdf import FPDF
import base64
from datetime import datetime

# --- 1. GLOBAL DATA (Fixed line 73 NameErrors) ---
# Defining these outside the 'if' block ensures they are always available.
AUDIT_SECTIONS = {
    "1. Physical Architecture": {
        "intro": "Validates silicon-to-ball delays and bank group configurations.",
        "df": pd.DataFrame({
            "Feature": ["Density", "Package", "Bank Groups", "Pkg Delay"],
            "Value": ["8Gb (512Mx16)", "96-FBGA", "2 Groups", "75 ps"],
            "Spec": ["Standard", "Standard", "x16 Type", "100ps Max"],
            "Significance": ["Total addressable space.", "Land pattern design.", "Interleaving efficiency.", "Trace matching offset."]
        })
    },
    "2. DC Power": {
        "intro": "Audits voltage rail tolerances to prevent bit-flip errors.",
        "df": pd.DataFrame({
            "Feature": ["VDD", "VPP", "VMAX", "IDD6N"],
            "Value": ["1.20V", "2.50V", "1.50V", "22 mA"],
            "Spec": ["1.26V Max", "2.75V Max", "1.50V Max", "30mA Max"],
            "Significance": ["Core stability.", "Row boost voltage.", "Absolute stress limit.", "Standby battery life."]
        })
    },
    "3. AC Timing": {
        "intro": "Analyzes signal integrity and clock period margins.",
        "df": pd.DataFrame({
            "Feature": ["tCK", "tAA", "tRFC", "Slew Rate"],
            "Value": ["625 ps", "13.75 ns", "350 ns", "5.0 V/ns"],
            "Spec": ["625ps Min", "13.75ns Max", "350ns Std", "4V/ns Min"],
            "Significance": ["3200 MT/s limit.", "Read latency.", "Refresh cycle window.", "Data Eye sharpness."]
        })
    },
    "4. Thermal Reliability": {
        "intro": "Validates refresh scaling for data retention at high temperatures.",
        "df": pd.DataFrame({
            "Feature": ["T-Case Max", "Normal Ref", "Extended Ref", "ASR"],
            "Value": ["95C", "1X (0-85C)", "2X (85-95C)", "Supported"],
            "Spec": ["JEDEC Limit", "7.8us", "3.9us", "Optional"],
            "Significance": ["Shutdown point.", "Standard retention.", "Heat leakage fix.", "Auto power mgmt."]
        })
    },
    "5. Advanced Integrity": {
        
