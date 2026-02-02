import streamlit as st
import pandas as pd
from fpdf import FPDF
from datetime import datetime

# --- 1. DATA STRUCTURE (Restored & Crash-Proofed) ---
AUDIT_DATA = {
    "1. Physical Architecture": {
        "intro": "Validates package-to-die mapping and bank group configurations.",
        "df": pd.DataFrame({
            "Feature": ["Density", "Package", "Bank Groups", "Pkg Delay"],
            "Value": ["8Gb (512Mx16)", "96-FBGA", "2 Groups", "75 ps"],
            "Spec": ["JESD79-4B", "Standard", "x16 Type", "100ps Max"],
            "Significance": ["Address mapping/bit-ordering", "Thermal footprint/PCB routing", "tCCD_S timing constraints", "Signal sync fly-by topology"]
        })
    },
    "2. DC Power Rails": {
        "intro": "Analyzes electrical rails for JEDEC safe operating areas.",
        "df": pd.DataFrame({
            "Feature": ["VDD", "VPP", "VrefDQ", "IDD6N"],
            "Value": ["1.20V", "2.50V", "0.72V", "22 mA"],
            "Spec": ["1.14-1.26V", "2.37-2.75V", "0.6*VDD", "30mA Max"],
            "Significance": ["Logic stability; prevents meta-stability", "Wordline boost; opens access gates", "DQ receiver sampling accuracy", "Standby data integrity current"]
        })
    },
    "3. AC Timing Parameters": {
        "intro": "Audits temporal boundaries for memory clock and strobes.",
        "df": pd.DataFrame({
            "Feature": ["tCK (avg)", "tAA", "tRCD", "tRP"],
            "Value": ["0.938 ns", "13.5 ns", "13.5 ns", "13.5 ns"],
            "Spec": [">0.937ns", "13.5ns Min", "13.5ns Min", "13.5ns Min"],
            "Significance": ["Clock period for speed binning", "READ command to first bit delay", "ACTIVATE to READ/WRITE delay", "Row Precharge bitline equalization"]
        })
    },
    "4. Thermal & Reliability": {
        "intro": "Reviews thermal envelopes and refresh rate scaling.",
        "df": pd.DataFrame({
            "Feature": ["T-Oper", "T-Storage", "tREFI", "Thermal Sensor"],
            "Value": ["0 to 95 C", "-55 to 100
                      
