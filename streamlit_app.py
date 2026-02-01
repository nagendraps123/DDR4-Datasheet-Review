import streamlit as st
import pandas as pd
import re
from PyPDF2 import PdfReader
from fpdf import FPDF
import base64

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="DDR4 JEDEC Professional Auditor", layout="wide")

# --- PDF GENERATION ENGINE (Synchronized Row Logic) ---
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
        headers = list(df.columns)
        
        for i in range(len(headers)):
            self.cell(col_widths[i], 10, headers[i], 1, 0, 'C')
        self.ln()
        
        self.set_font('Arial', '', 7)
        for _, row in df.iterrows():
            text_to_wrap = str(row[3])
            line_count = (self.get_string_width(text_to_wrap) / (col_widths[3] - 2)) + 1
            row_height = max(8, int(line_count) * 5) 

            x, y = self.get_x(), self.get_y()
            self.cell(col_widths[0], row_height, str(row[0]), 1)
            self.cell(col_widths[1], row_height, str(row[1]), 1)
            self.cell(col_widths[2], row_height, str(row[2]), 1)
            
            self.multi_cell(col_widths[3], 5, text_to_wrap, 1)
            
