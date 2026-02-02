import streamlit as st
import pandas as pd
import re
from PyPDF2 import PdfReader
from fpdf import FPDF
import base64

# --- 1. GLOBAL AUDIT DATA ---
AUDIT_DATA = {
    "Architecture": {
        "about": "Validates physical silicon-to-package mapping and signal skew offsets.",
        "df": pd.DataFrame({
            "Feature": ["Density", "Package", "Bank Groups", "Pkg Delay"],
            "Value": ["8Gb (512Mx16)", "96-FBGA", "2 Groups", "75 ps"],
            "Spec": ["Standard", "Standard", "x16 Type", "100ps Max"],
            "Significance": ["Determines total addressable memory space.", "Defines physical land pattern for PCB mounting.", "Impacts interleaving efficiency.", "Internal delay requiring trace matching."]
        })
    },
    "DC Power": {
        "about": "Audits voltage rail tolerances and maximum stress limits.",
        "df": pd.DataFrame({
            "Feature": ["VDD", "VPP", "VMAX", "IDD6N"],
            "Value": ["1.20V", "2.50V", "1.50V", "22 mA"],
            "Spec": ["1.26V Max", "2.75V Max", "1.50V Max", "30mA Max"],
            "Significance": ["Core stability; ripple >5% causes bit-flips.", "Wordline boost voltage for row activation.", "Absolute maximum stress limit.", "Standby current consumption."]
        })
    },
    "AC Timing": {
        "about": "Verifies speed-bin compliance and CAS latency (tAA) margins.",
        "df": pd.DataFrame({
            "Feature": ["tCK", "tAA", "tRFC", "Slew Rate"],
            "Value": ["625 ps", "13.75 ns", "350 ns", "5.0 V/ns"],
            "Spec": ["625ps Min", "13.75ns Max", "350ns Std", "4V/ns Min"],
            "Significance": ["Clock period for 3200 MT/s operation.", "Read command to valid data latency.", "Refresh cycle window required for retention.", "Signal sharpness for data eye closure."]
        })
    },
    "Thermal": {
        "about": "Validates refresh rate scaling (tREFI) for high-temperature reliability.",
        "df": pd.DataFrame({
            "Feature": ["T-Case Max", "Normal Ref", "Extended Ref", "tREFI (85C)"],
            "Value": ["95C", "1X (0-85C)", "2X (85-95C)", "3.9 us"],
            "Spec": ["JEDEC Limit", "7.8us Interval", "3.9us Interval", "Standard"],
            "Significance": ["Absolute thermal ceiling for operation.", "Standard interval for room temperature.", "2X scaling required for heat leakage.", "Calculated frequency for data maintenance."]
        })
    },
    "Integrity": {
        "about": "Audits reliability features like CRC and DBI to mitigate bus noise.",
        "df": pd.DataFrame({
            "Feature": ["CRC", "DBI", "Parity", "PPR"],
            "Value": ["Yes", "Yes", "Yes", "Yes"],
            "Spec": ["Optional", "Optional", "Optional", "Optional"],
            "Significance": ["Detects data transmission errors.", "Reduces switching noise and power.", "Command/Address error detection.", "Field repair for faulty cell rows."]
        })
    }
}

SOLUTIONS = {
    "Thermal Risk": "Implement BIOS-level 'Fine Granularity Refresh' to scale tREFI to 3.9us at T-Case > 85C.",
    "Skew Risk": "Apply 75ps Pkg Delay compensation into the PCB layout routing constraints.",
    "Signal Integrity": "Enable Data Bus Inversion (DBI) and CRC in the controller for high-EMI stability
    
