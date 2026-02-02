import streamlit as st
import pandas as pd
from fpdf import FPDF
from datetime import datetime

# --- 1. GLOBAL AUDIT DATA (With Expanded Technical Detail) ---
AUDIT_SECTIONS = {
    "1. Physical Architecture": {
        "intro": """This section validates the physical mapping of the silicon die to the PCB package. 
        It ensures that the 'Package Delay' (the time signal takes to travel from the silicon ball to the internal die) 
        is within the skew limits to prevent data corruption at high frequencies.""",
        "df": pd.DataFrame({
            "Feature": ["Density", "Package", "Bank Groups", "Pkg Delay"],
            "Value": ["8Gb (512Mx16)", "96-FBGA", "2 Groups", "75 ps"],
            "Spec": ["Standard", "Standard", "x16 Type", "100ps Max"],
            "Significance": [
                "Total addressable bits; defines the memory capacity per rank.",
                "The physical footprint; 96-ball Fine Pitch Ball Grid Array.",
                "Separation of banks to allow independent access and higher bandwidth.",
                "Internal trace propagation delay; must be matched to prevent signal skew."
            ]
        })
    },
    "2. DC Power": {
        "intro": """Analyzes the electrical stability of the memory module. Memory cells require 
        precise voltage levels to maintain charge; even minor 'ripples' or noise on these rails 
        can lead to 'bit-flips' or permanent lattice damage in the silicon.""",
        "df": pd.DataFrame({
            "Feature": ["VDD", "VPP", "VMAX", "IDD6N"],
            "Value": ["1.20V", "2.50V", "1.50V", "22 mA"],
            "Spec": ["1.26V Max", "2.75V Max", "1.50V Max", "30mA Max"],
            "Significance": [
                "Core logic voltage; fluctuations >5% cause logic state instability.",
                "Wordline boost voltage; essential for accessing the memory array.",
                "Absolute maximum voltage before physical transistor breakdown occurs.",
                "Current draw during self-refresh; critical for battery-operated power budgets."
            ]
        })
    },
    "3. Timing Parameters": {
        "intro": """Timing is the heartbeat of the DRAM. This section reviews the speed at which 
        the memory can open rows, read data, and close rows. These are measured in clock cycles 
        or nanoseconds (ns).""",
        "df": pd.DataFrame({
            "Feature": ["tCK (avg)", "tCL", "
                        
