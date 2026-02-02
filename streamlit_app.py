import streamlit as st
import pandas as pd
import re
from PyPDF2 import PdfReader
from fpdf import FPDF
import base64

# --- 1. GLOBAL AUDIT DATA (All 5 Sections Restored) ---
AUDIT_DATA = {
    "Architecture": {
        "about": "Validates the physical silicon-to-package mapping. It ensures that internal package delays (Pkg Delay) are matched across the data bus.",
        "df": pd.DataFrame({
            "Feature": ["Density", "Package", "Bank Groups", "Pkg Delay"],
            "Value": ["8Gb (512Mx16)", "96-FBGA", "2 Groups", "75 ps"],
            "Spec": ["Standard", "Standard", "x16 Type", "100ps Max"],
            "Significance": ["Determines addressable space.", "Land pattern design.", "Interleaving efficiency.", "Trace offset matching."]
        })
    },
    "DC Power": {
        "about": "Analyzes voltage rail tolerances (VDD, VPP) and maximum stress limits to prevent bit-flips.",
        "df": pd.DataFrame({
            "Feature": ["VDD", "VPP", "VMAX", "IDD6N"],
            "Value": ["1.20V", "2.50V", "1.50V", "22 mA"],
            "Spec": ["1.26V Max", "2.75V Max", "1.50V Max", "30mA Max"],
            "Significance": ["Core stability.", "Row boost voltage.", "Absolute stress limit.", "Standby battery life."]
        })
    },
    "AC Timing": {
        "about": "Verifies speed-bin compliance (e.g., 3200 MT/s). Audits clock period (tCK) and CAS latency (tAA).",
        "df": pd.DataFrame({
            "Feature": ["tCK", "tAA", "tRFC", "Slew Rate"],
            "Value": ["625 ps", "13.75 ns", "350 ns", "5.0 V/ns"],
            "Spec": ["625ps Min", "13.75ns
                     
