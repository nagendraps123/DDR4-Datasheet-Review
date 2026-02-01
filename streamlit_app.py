import streamlit as st
import pandas as pd
import re
from PyPDF2 import PdfReader
from fpdf import FPDF
import base64

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="DDR4 JEDEC Professional Auditor", layout="wide")

# --- PROFESSIONAL PDF ENGINE ---
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
        for i, col in enumerate(df.columns):
            self.cell(col_widths[i], 10, col, 1, 0, 'C')
        self.ln()
        
        self.set_font('Arial', '', 7)
        for _, row in df.iterrows():
            text = str(row.iloc[3])
            # Sync row height based on detailed notes column
            line_count = (self.get_string_width(text) / (col_widths[3] - 2)) + 1
            row_height = max(8, int(line_count) * 4.5) 

            start_x, start_y = self.get_x(), self.get_y()
            self.cell(col_widths[0], row_height, str(row.iloc[0]), 1)
            self.cell(col_widths[1], row_height, str(row.iloc[1]), 1)
            self.cell(col_widths[2], row_height, str(row.iloc[2]), 1)
            self.multi_cell(col_widths[3], row_height / int(line_count) if int(line_count) > 0 else row_height, text, 1)
            self.set_xy(start_x, start_y + row_height)

def extract_val(text, patterns, default="TBD"):
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match: return match.group(1)
    return default

# --- RESTORED DETAILED INTRODUCTION ---
st.title("🔬 DDR4 JEDEC Professional Compliance Auditor")
st.markdown("""
### **Introduction**
The **DDR4 JEDEC Professional Compliance Auditor** is a specialized engineering tool designed to automate the validation of memory device datasheets against the industry-standard **JESD79-4B** specifications.

**Core Capabilities:**
* **Automated Extraction:** Scans PDF datasheets for critical silicon parameters ($tCK$, $VDD$, $Pkg Delay$).
* **Compliance Mapping:** Cross-references values against JEDEC-mandated limits.
*
            
