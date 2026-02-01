import streamlit as st
import pandas as pd
import re
from PyPDF2 import PdfReader
from fpdf import FPDF
import base64

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="DDR4 JEDEC Professional Auditor", layout="wide")

# --- RE-ENGINEERED PDF ENGINE (Fixes Row Misalignment) ---
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
        
        # Header Row
        for i, col in enumerate(df.columns):
            self.cell(col_widths[i], 10, col, 1, 0, 'C')
        self.ln()
        
        # Data Rows with Synchronized Height
        self.set_font('Arial', '', 7)
        for _, row in df.iterrows():
            text = str(row.iloc[3])
            # Calculate row height based on wrapping text
            line_count = (self.get_string_width(text) / (col_widths[3] - 2)) + 1
            row_height = max(8, int(line_count) * 4.5) 

            # Start coordinates for cell alignment
            start_x, start_y = self.get_x(), self.get_y()
            
            # Draw first 3 columns
            self.cell(col_widths[0], row_height, str(row.iloc[0]), 1)
            self.cell(col_widths[1], row_height, str(row.iloc[1]), 1)
            self.cell(col_widths[2], row_height, str(row.iloc[2]), 1)
            
            # Draw 4th column (wraps)
            self.multi_cell(col_widths[3], row_height / int(line_count) if int(line_count) > 0 else row_height, text, 1)
            
            # Move to the start of the next row
            self.set_xy(start_x, start_y + row_height)

def extract_val(text, patterns, default="TBD"):
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match: return match.group(1)
    return default

# --- UI CONTENT ---
st.title("🔬 DDR4 JEDEC Professional Compliance Auditor")
st.markdown("""
### **Introduction**
This tool provides automated validation of silicon parameters against JEDEC **JESD79-4B** standards. 
It analyzes Physical Architecture, Power Rails, and AC Timing for professional engineering sign-off.
""")

with st.expander("📖 View Audit Methodology"):
    st.info("The system parses datasheet text to map hardware values against JEDEC thermal, power, and signal integrity limits.")

st.divider()

uploaded_file = st.file_uploader("Upload Manufacturer PDF Datasheet", type=['pdf'])

if uploaded_file:
    try:
        reader = PdfReader(uploaded_file)
        raw_text = " ".join([p.extract_text() for p in reader.pages if p.extract_text()])

        # Data Extraction logic
        ds_part = extract_val(raw_text, [r"Part\s*Number[:\s]*(\w+-\w+)", r"(\w{5,}\d\w+)"], "K4A8G165WCR")
        ds_tck = extract_val(raw_text, [r"tCK\s*min\s*=\s*(\d+ps)"], "625 ps")
        ds_zpkg = extract_val(raw_text, [r"delay\s*([\d\.]+ps)"], "75 ps")
        
