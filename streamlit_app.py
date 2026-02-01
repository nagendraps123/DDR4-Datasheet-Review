import streamlit as st
import pandas as pd
import re
from PyPDF2 import PdfReader
from fpdf import FPDF
import base64
from datetime import datetime

# --- PAGE CONFIG ---
st.set_page_config(page_title="DDR4 JEDEC Professional Auditor", layout="wide")

# --- PROFESSIONAL PDF ENGINE ---
class JEDEC_PDF(FPDF):
    def __init__(self, project_name="N/A", part_number="TBD"):
        super().__init__()
        self.project_name = project_name
        self.part_number = part_number

    def header(self):
        self.set_font('Arial', 'B', 16)
        self.cell(0, 10, 'DDR4 JEDEC Professional Compliance Audit', 0, 1, 'C')
        self.set_font('Arial', '', 10)
        h_info = f"Project: {self.project_name} | Device PN: {self.part_number}"
        self.cell(0, 7, h_info, 0, 1, 'C')
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        d_str = datetime.now().strftime("%Y-%m-%d %H:%M")
        f_text = f"PN: {self.part_number} | Generated: {d_str} | Page {self.page_no()}"
        self.cell(0, 10, f_text, 0, 0, 'C')

    def add_intro_box(self, text):
        self.set_font('Arial', 'B', 11)
        self.cell(0, 8, "Report Introduction", 0, 1, 'L')
        self.set_font('Arial', '', 9)
        self.multi_cell(0, 5, text)
        self.ln(5)

    def add_section_header(self, title, intro):
        self.set_font('Arial', 'B', 11)
        self.set_fill_color(235, 235, 235)
        self.cell(0, 8, ' ' + title, 0, 1, 'L', 1)
        self.set_font('Arial', 'I', 8)
        self.multi_cell(0, 4, intro)
        self.ln(2)

    def create_table(self, df):
        self.set_font('Arial', 'B', 8)
        w = [30, 25, 30, 105]
        cols = ["Feature", "Value", "Spec/Limit", "Significance"]
        for i, col in enumerate(cols):
            self.cell(w[i], 8, col, 1, 0, 'C')
        self.ln()
        self.set_font('Arial', '', 7)
        for _, row in df.iterrows():
            text = str(row.iloc[3])
            h = 14 if len(text) > 65 else 8
            x, y = self.get_x(), self.get_y()
            self.cell(w[0], h, str(row.iloc[0]), 1)
            self.cell(w[1], h, str(row.iloc[1]), 1)
            self.cell(w[2], h, str(row.iloc[2]), 1)
            self.multi_cell(w[3], h/2 if len(text) > 65 else h, text, 1)
            self.set_xy(x, y + h)
        self.ln(3)

def extract_val(text, patterns, default="TBD"):
    for p in patterns:
        m = re.search(p, text, re.IGNORECASE)
        if m: return m.group(1)
    return default

# --- UI CONTENT ---
st.title("🔬 DDR4 JEDEC Professional Compliance Auditor")

intro_text = "The DDR4 JEDEC Professional Compliance Auditor validates memory device datasheets against the JESD79-4B specification. This system audits physical architecture, DC power rails, AC timing, thermal reliability, and integrity features."

st.markdown("### **Introduction**")
st.info(intro_text)

p_name = st.text_input("Hardware Project Name", "DDR4-Analysis-Project")
file = st.file_uploader("Upload Manufacturer PDF Datasheet", type=['pdf'])

if file:
    try:
        reader = PdfReader(file)
        raw_text = "".join([p.extract_text() for p in reader.pages if p.extract_text()])
        
        # Core Variable Definitions to prevent NameError
        pn = extract_val(raw_text, [r"Part\s*Number[:\s]*(\w+-\w+)", r"(\w{5,}\d\w+)"], "K4A8G165WCR")
        tck
        
