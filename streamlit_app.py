import streamlit as st
import pandas as pd
import pdfplumber
from fpdf import FPDF
from datetime import datetime
import re
import io

# --- 1. CONFIG & CONSTANTS ---
st.set_page_config(page_title="JEDEC Automated Audit", layout="wide", page_icon="🛡️")

# JEDEC JESD79-4 Standard Lookups
TRFC_MAP = {
    "2Gb": 160, "4Gb": 260, "8Gb": 350, "16Gb": 550, "32Gb": 850
}

# --- 2. EXTRACTION & AUDIT ENGINE ---
def extract_data(uploaded_file):
    text = ""
    file_bytes = uploaded_file.getvalue() 
    try:
        with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
            for page in pdf.pages[:15]:
                content = page.extract_text()
                if content:
                    text += content + "\n"
    except Exception as e:
        st.error(f"Text Extraction Error: {e}")
    return text
    
