import streamlit as st
import pandas as pd
import re
from PyPDF2 import PdfReader
from fpdf import FPDF
import base64

# --- PAGE SETUP ---
st.set_page_config(page_title="DDR4 JEDEC Auditor", layout="wide")

# --- PDF GENERATOR ---
class JEDEC_PDF(FPDF):
    def __init__(self, project_name="N/A"):
        super().__init__()
        self.project_name = project_name

    def header(self):
        self.set_font('Arial', 'B', 16)
        self.cell(0, 10, 'DDR4 JEDEC Professional Compliance Audit', 0, 1, 'C')
        self.set_font('Arial', '', 10)
        self.cell(0, 7, 'Project: ' + str(self.project_name), 0, 1, 'C')
        self.ln(10)

    def create_table(self, title, df):
        self.set_font('Arial', 'B', 12)
        self.cell(0, 10, title, 0, 1, 'L')
        self.set_font('Arial', 'B', 8)
        w = [30, 30, 30, 100]
        for i, col in enumerate(df.columns):
            self.cell(w[i], 10, col, 1, 0, 'C')
        self.ln()
        self.set_font('Arial', '', 7)
        for _, row in df.iterrows():
            text = str(row.iloc[3])
            # Calculate height
            h = 10 if len(text) < 60 else 15
            x, y = self.get_x(), self.get_y()
            self.cell(w[0], h, str(row.iloc[0]), 1)
            self.cell(w[1], h, str(row.iloc[1]), 1)
            self.cell(w[2], h, str(row.iloc[2]), 1)
            self.multi_cell(w[3], h/2 if len(text) > 60 else h, text, 1)
            self.set_xy(x, y + h)
        self.ln(5)
        
