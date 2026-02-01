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
    def __init__(self, project_name="N/A"):
        super().__init__()
        self.project_name = project_name

    def header(self):
        self.set_font('Arial', 'B', 16)
        self.cell(0, 10, 'DDR4 JEDEC Professional Compliance Audit', 0, 1, 'C')
        self.set_font('Arial', '', 10)
        self.cell(0, 7, f'Project: {self.project_name} | Standard: JESD79-4B', 0, 1, 'C')
        self.cell(0, 7, 'Status: Official Engineering Report', 0, 1, 'C')
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
            line_count = (self.get_string_width(text) / (col_widths[3] - 2)) + 1
            row_height = max(8, int(line_count) * 4.5) 

            start_x, start_y = self.get_x(), self.get_y()
            self.cell(col_widths[0], row_height, str(row.iloc[0]), 1)
            self.cell(col_widths[1], row_height, str(row.iloc[1]), 1)
            self.cell(col_widths[2], row_height, str(row.iloc[2]),
            
