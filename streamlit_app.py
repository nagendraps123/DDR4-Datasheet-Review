import streamlit as st
import pandas as pd
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
        "intro": "Validates the silicon-to-package interface and signal path matching (Pkg Delay) to ensure timing skew remains within JEDEC boundaries.",
        "df": pd.DataFrame({
            "Feature": ["Density", "Package", "Bank Groups", "Pkg Delay"],
            "Value": ["8Gb (512Mx16)", "96-FBGA", "2 Groups", "75 ps"],
            "Spec": ["JESD79-4 Compliant", "Standard", "x16 Type", "100ps Max"],
            "Significance": [
                "Address mapping; affects Row/Column/Bank bit-ordering for controller addressing.",
                "Ball pitch and layout; dictates the escape routing and PCB impedance control requirements.",
                "Enables Bank Group (BG) interleaving to satisfy tCCD_S timing constraints for high bandwidth.",
                "Silicon-to-package trace length; exceeding 100ps breaks signal fly-by topology synchronicity."
            ]
