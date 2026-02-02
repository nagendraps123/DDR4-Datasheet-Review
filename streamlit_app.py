import streamlit as st
import pandas as pd
from PyPDF2 import PdfReader
from fpdf import FPDF
from datetime import datetime

# --- 1. PDF CLASS WITH HEADER/FOOTER ---
class DRAM_Report(FPDF):
    def __init__(self, part_number):
        super().__init__()
        self.part_number = part_number

    def header(self):
        self.set_font("Arial", 'B', 10)
        self.cell(0, 10, f"DDR Compliance Audit | Part No: {self.part_number}", 0, 1, 'R')
        self.line(10, 18, 200, 18)

    def footer(self):
        self.set_y(-15)
        self.set_font("Arial", 'I', 8)
        self.cell(0, 10, f"Page {self.page_no()} | Part Number: {self.part_number}", 0, 0, 'C')

# --- 2. GLOBAL AUDIT DATA ---
AUDIT_SECTIONS = {
    "1. Physical Architecture": {
        "intro": "Validates silicon-to-ball delays and bank group configurations.",
        "df": pd.DataFrame({
            "Feature": ["Density", "Package", "Bank Groups", "Pkg Delay"],
            "Value": ["8Gb (512Mx16)", "96-FBGA", "2 Groups", "75 ps"],
            "Spec": ["Standard", "Standard", "x16 Type", "100ps Max"],
            "Significance": ["Addressable space", "Physical footprint", "Interleaving", "Internal delay"]
        })
    },
    "2. DC Power": {
        "intro": "Audits voltage rail tolerances (VDD, VPP) to prevent bit-flips.",
        "df": pd.DataFrame({
            "Feature": ["VDD", "VPP", "VMAX", "IDD6N"],
            "Value": ["1.20V", "2.50V", "1.50V", "22 mA"],
            "Spec": ["1.26V Max", "2.75V Max", "1.50V Max", "30mA Max"],
            "Significance": ["Core stability", "Wordline boost", "Safety rating", "Refresh current"]
        })
    },
    "3. Timing Parameters": {
        "intro": "Analyzes critical clock cycles and data strobe latencies.",
        "df": pd.DataFrame({
            "Feature": ["tCK (avg)", "tCL", "tRCD", "tRP"],
            "Value": ["0.938 ns", "16 cycles", "16 cycles", "16 cycles"],
            "Spec": ["0.937ns Min", "CL=16", "tRCD=16", "tRP=16"],
            "Significance": ["Clock frequency", "Read latency", "RAS-CAS delay", "Precharge"]
        })
    },
    "4. Thermal & Environmental": {
        "intro": "Reviews operating temperature ranges and refresh scaling.",
        "df": pd.DataFrame({
            "Feature": ["T-Oper", "T-Storage", "Refresh Rate", "Thermal Sensor"],
            "Value": ["0 to 95 C
                      
