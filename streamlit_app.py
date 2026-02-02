import streamlit as st
import pandas as pd
import re
from PyPDF2 import PdfReader
from fpdf import FPDF
import base64
from datetime import datetime

# --- 1. GLOBAL TOOL CONTENT (The "Agreed Content") ---
# Defining this at the top prevents NameErrors on lines 47, 73, 104, and 147.
AUDIT_SECTIONS = {
    "1. Physical Architecture": {
        "intro": "Validates silicon-to-ball delays (Pkg Delay) and bank group configurations.",
        "df": pd.DataFrame({
            "Feature": ["Density", "Package", "Bank Groups", "Pkg Delay"],
            "Value": ["8Gb (512Mx16)", "96-FBGA", "2 Groups", "75 ps"],
            "Spec": ["Standard", "Standard", "x16 Type", "100ps Max"],
            "Significance": ["Determines addressable memory space.", "Defines physical land pattern.", "Critical for interleaving efficiency.", "Internal silicon-to-ball delay offset."]
        })
    },
    "2. DC Power": {
        "intro": "Audits voltage rail tolerances (VDD, VPP) to prevent bit-flips and lattice stress.",
        "df": pd.DataFrame({
            "Feature": ["VDD", "VPP", "VMAX", "IDD6N"],
            "Value": ["1.20V", "2.50V", "1.50V", "22 mA"],
            "Spec": ["1.26V Max", "2.75V Max", "1.50V Max", "30mA Max"],
            "Significance": ["Core stability; ripple >5% causes errors.", "Wordline
                             
