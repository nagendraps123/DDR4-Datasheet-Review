import streamlit as st
import pandas as pd
import re
from PyPDF2 import PdfReader
from fpdf import FPDF
import base64

# --- 1. GLOBAL AUDIT DATA ---
AUDIT_DATA = {
    "Architecture": {
        "about": "Validates the physical silicon-to-package mapping and internal package delays.",
        "df": pd.DataFrame({
            "Feature": ["Density", "Package", "Bank Groups", "Pkg Delay"],
            "Value": ["8Gb (512Mx16)", "96-FBGA", "2 Groups", "75 ps"],
            "Spec": ["Standard", "Standard", "x16 Type", "100ps Max"],
            "Significance": ["Determines total addressable memory space and density for the system controller.", "Defines the physical land pattern and ball pitch for PCB manufacturing.", "Determines the number of independent bank accesses possible, impacting interleaving efficiency.", "Internal silicon-to-ball delay that must be compensated for in trace length matching."]
        })
    },
    "DC Power": {
        "about": "Audits voltage rail tolerances (VDD, VPP) and maximum stress limits.",
        "df": pd.DataFrame({
            "Feature": ["VDD", "VPP", "VMAX", "IDD6N"],
            "Value": ["1.20V", "2.50V", "1.50V", "22 mA"],
            "Spec": ["1.26V Max", "2.75V Max", "1.50V Max", "30mA Max"],
            "Significance": ["Core operating voltage; fluctuations exceeding JEDEC limits can cause logic bit-flips.", "High voltage wordline boost required for row activation; low VPP prevents proper cell opening.", "Absolute maximum voltage stress limit; exceeding this risks permanent oxide breakdown.", "Standby current consumption; critical for mobile/laptop battery life during sleep states."]
        })
    },
    "AC Timing": {
        "about": "Verifies speed-bin compliance and CAS latency (tAA) margins.",
        "df": pd.DataFrame({
            "Feature": ["tCK", "tAA", "tRFC", "Slew Rate"],
            "Value": ["625 ps", "13.75 ns", "350 ns", "5.0 V/ns"],
            "Spec": ["625ps Min", "13.75ns Max", "350ns Std", "4V/ns Min"],
            "Significance": ["Clock period for 3200 MT/s; defines the maximum throughput of the memory channel.", "Minimum time from Read command to valid data; direct impact on system responsiveness.", "Time required for a refresh cycle; essential for maintaining data integrity in the capacitor array.", "Sharpness of the signal transition; poor slew rate causes timing jitter and data eye closure."]
        })
    },
    "Thermal": {
        "about": "Validates refresh rate scaling (tREFI) for high-temperature reliability.",
        "df": pd.DataFrame({
            "Feature": ["T-Case Max", "Normal Ref", "Extended Ref", "tREFI (85C)"],
            "Value": ["95C", "1X (0-85C)", "2X (85-95C)", "3.9 us"],
            "Spec": ["JEDEC Limit", "7.8us
                     
