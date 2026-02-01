import streamlit as st
import pandas as pd
import re
from PyPDF2 import PdfReader
from fpdf import FPDF
import base64

# --- CONFIG ---
st.set_page_config(page_title="DDR4 JEDEC Professional Auditor", layout="wide")

# --- PDF ENGINE ---
class JEDEC_PDF(FPDF):
    def __init__(self, project_name="N/A"):
        super().__init__()
        self.project_name = project_name

    def header(self):
        self.set_font('Arial', 'B', 16)
        self.cell(0, 10, 'DDR4 JEDEC Professional Compliance Audit', 0, 1, 'C')
        self.set_font('Arial', '', 10)
        header_str = 'Project: ' + str(self.project_name) + ' | Standard: JESD79-4B'
        self.cell(0, 7, header_str, 0, 1, 'C')
        self.ln(10)

    def chapter_title(self, label):
        self.set_font('Arial', 'B', 12)
        self.set_fill_color(230, 230, 230)
        self.cell(0, 10, ' ' + str(label), 0, 1, 'L', 1)
        self.ln(2)

    def create_table(self, df):
        self.set_font('Arial', 'B', 8)
        widths = [30, 30, 30, 100]
        for i, col in enumerate(df.columns):
            self.cell(widths[i], 10, col, 1, 0, 'C')
        self.ln()
        self.set_font('Arial', '', 7)
        for _, row in df.iterrows():
            text = str(row.iloc[3])
            line_count = (self.get_string_width(text) / (widths[3] - 2)) + 1
            h = max(8, int(line_count) * 5)
            curr_x, curr
            
