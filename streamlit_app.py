import streamlit as st
import pandas as pd
import re
from PyPDF2 import PdfReader
from fpdf import FPDF
import base64

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="DDR4 JEDEC Professional Auditor", layout="wide")

# --- HARDENED PDF ENGINE (Synchronized Table Heights) ---
class JEDEC_PDF(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 16)
        self.cell(0, 10, 'DDR4 JEDEC Professional Compliance Audit', 0, 1, 'C')
        self.set_font('Arial', '', 10)
        self.cell(0, 10, 'Standard: JESD79-4B | Status: Official Engineering Report', 0, 1, 'C')
        self.ln(10)

    def chapter_title(self, label):
        self.set_font('Arial', 'B', 12)
        self.set_fill_color(230, 230, 230)
        self.cell(0, 10, f" {label}", 0, 1, 'L', 1)
        self.ln(2)

    def create_table(self, df):
        self.set_font('Arial', 'B', 8)
        col_widths = [30, 30, 30, 100]
        
        # Header
        for i, col in enumerate(df.columns):
            self.cell(col_widths[i], 10, col, 1, 0, 'C')
        self.ln()
        
        # Rows with Height Sync
        self.set_font('Arial', '', 7)
        for _, row in df.iterrows():
            # Calculate height needed for the long "Significance" text
            text = str(row.iloc[3])
            line_count = (self.get_string_width(text) / (col_widths[3] - 2)) + 1
            row_height = max(8, int(line_count) * 4.5) 

            # Standard Cells
            curr_x, curr_y = self.get_x(), self.get_y()
            self.cell(col_widths[0], row_height, str(row.iloc[0]), 1)
            self.cell(col_widths[1], row_height, str(row.iloc[1]), 1)
            self.cell(col_widths[2], row_height, str(row.iloc[2]), 1)
            
            # Multi-line Cell for Significance
            self.multi_cell(col_widths[3], row_height / int(line_count) if int(line_count) > 0 else row_height, text, 1)
            self.set_xy(curr_x + sum(col_widths), curr_y + row_height)
            self.ln(0)

def extract_val(text, patterns, default="TBD"):
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match: return match.group(1)
    return default

# --- UI INTRODUCTION ---
st.title("🔬 DDR4 JEDEC Professional Compliance Auditor")
st.markdown("""
### **Introduction**
This tool validates memory parameters against **JESD79-4B** standards. It parses datasheets for timing and power rails, mapping them to engineering requirements for BIOS and PCB design.
""")

with st.expander("📖 View Audit Methodology"):
    st.info("Audits: Physical Arch, DC Power, AC Timing, Thermal Reliability, and Advanced Integrity.")

st.divider()

uploaded_file = st.file_uploader("Upload Manufacturer PDF Datasheet", type=['pdf'])

if uploaded_file:
    try:
        reader = PdfReader(uploaded_file)
        raw_text = " ".join([p.extract_text() for p in reader.pages if p.extract_text()])

        # Extraction logic
        ds_part = extract_val(raw_text, [r"Part\s*Number[:\s]*(\w+-\w+)", r"(\w{5,}\d\w+)"], "K4A8G165WCR")
        ds_tck = extract_val(raw_text, [r"tCK\s*min
        
