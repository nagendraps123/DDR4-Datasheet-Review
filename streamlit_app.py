import streamlit as st
import pandas as pd
from fpdf import FPDF
from datetime import datetime

# --- 1. GLOBAL DATA STRUCTURE (Triple-Quoted for Safety) ---
AUDIT_DATA = {
    "1. Physical Architecture": {
        "intro": """Analyzes silicon-to-package delay offsets and bank group configurations.""",
        "df": pd.DataFrame({
            "Feature": ["Density", "Package", "Bank Groups", "Pkg Delay"],
            "Value": ["8Gb (512Mx16)", "96-FBGA", "2 Groups", "75 ps"],
            "Spec": ["Standard", "Standard", "x16 Type", "100ps Max"],
            "Significance": ["Addressable space", "Physical footprint", "Interleaving", "Internal delay"]
        })
    },
    "2. DC Power": {
        "intro": """Audits voltage rail tolerances (VDD, VPP) to prevent bit-flips.""",
        "df": pd.DataFrame({
            "Feature": ["VDD", "VPP", "VMAX", "IDD6N"],
            "Value": ["1.20V", "2.50V", "1.50V", "22 mA"],
            "Spec": ["1.14V-1.26V", "2.375V-2.75V", "1.50V Max", "30mA Max"],
            "Significance": ["Core stability", "Wordline boost", "Safety rating", "Refresh current"]
        })
    },
    "3. Timing Parameters": {
        "intro": """Analyzes critical clock cycles and data strobe latencies.""",
        "df": pd.DataFrame({
            "Feature": ["tCK (avg)", "tCL", "tRCD", "tRP"],
            "Value": ["0.938 ns", "16 cycles", "16 cycles", "16 cycles"],
            "Spec": ["0.937ns Min", "CL=16", "tRCD=16", "tRP=16"],
            "Significance": ["Clock frequency", "Read latency", "RAS-CAS delay", "Precharge"]
        })
    },
    "4. Thermal & Environmental": {
        "intro": """Reviews operating temperature ranges and refresh scaling.""",
        "df": pd.DataFrame({
            "Feature": ["T-Oper", "T-Storage", "Refresh Rate", "Thermal Sensor"],
            "Value": ["0 to 95 C", "-55 to 100 C", "64ms @ <85C", "Integrated"],
            "Spec": ["0 to 95 C", "Standard", "32ms @ >85C", "JEDEC Compliant"],
            "Significance": ["Safe window", "Storage limit", "Heat integrity", "Monitoring"]
        })
    },
    "5. Command & Address": {
        "intro": """Evaluates command bus signaling and parity checking.""",
        "df": pd.DataFrame({
            "Feature": ["C/A Latency", "CA Parity", "CRC Error", "DBI"],
            "Value": ["Disabled", "Enabled", "Auto-Retry", "Enabled"],
            "Spec": ["Optional", "Required", "Optional", "x
                     
