import streamlit as st
import pandas as pd
import pdfplumber
from fpdf import FPDF
from datetime import datetime
import re
import os
# New imports for OCR
from pdf2image import convert_from_bytes
import pytesseract
import numpy as np

# --- 1. CONFIG & README ---
st.set_page_config(page_title="JEDEC Automated Audit", layout="wide", page_icon="🛡️")

def load_readme():
    if os.path.exists("README.md"):
        with open("README.md", "r", encoding="utf-8") as f:
            return f.read()
    return "README.md not found."

with st.sidebar:
    st.title("System Controls")
    use_ocr = st.checkbox("Enable OCR (For Scanned PDFs)", value=False)
    if st.checkbox("Show Tool Documentation"):
        st.markdown(load_readme())
    st.divider()
    st.caption("Engine: Gemini 3 Flash + OCR Hybrid")

st.title("🛡️ Dynamic DRAM Compliance Audit")

# --- 2. EXTRACTION ENGINE (Hybrid: Text + OCR) ---
def extract_data(file_bytes, ocr_enabled):
    text = ""
    # Try standard extraction first
    try:
        with pdfplumber.open(file_bytes) as pdf:
            for page in pdf.pages[:10]:
                content = page.extract_text()
                if content:
                    text += content + "\n"
    except:
        pass

    # If text is empty and OCR is enabled, perform OCR
    if len(text.strip()) < 50 and ocr_enabled:
        with st.spinner("Performing OCR on scanned pages..."):
            images = convert_from_bytes(file_bytes.read())
            for img in images[:5]: # Limit to 5 pages for speed
                text += pytesseract.image_to_string(img) + "\n"
    return text

def run_audit(text):
    results = {
        "VDD": re.search(r"VDD\s*[:=]?\s*([\d\.]+V)", text, re.IGNORECASE),
        "tAA": re.search(r"tAA\s*.*?\s*([\d\.]+ns)", text, re.IGNORECASE),
        "tRP": re.search(r"tRP\s*.*?\s*([\d\.]+ns)", text, re.IGNORECASE),
        "Density": re.search(r"(\d+Gb|\d+Mb)", text),
        "CRC": "CRC" in text.upper(),
        "Parity": "PARITY" in text.upper() or "C/A PARITY" in text.upper()
    }
    return results

# --- 3. INPUTS ---
col_in1, col_in2 = st.columns(2)
with col_in1:
    uploaded_file = st.file_uploader("Upload JEDEC Datasheet (PDF)", type="pdf")
with col_in2:
    part_no = st.text_input("Enter Part Number", placeholder="e.g. K4A8
                            
