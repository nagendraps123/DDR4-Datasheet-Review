import streamlit as st
import pandas as pd
import pdfplumber
from fpdf import FPDF
from datetime import datetime
import re
import io

# --- 1. CONFIG & CONSTANTS ---
st.set_page_config(page_title="JEDEC Automated Audit", layout="wide", page_icon="🛡️")

# JEDEC JESD79-4 Refresh Cycle Time (tRFC) Mapping (in nanoseconds)
TRFC_MAP = {
    "2Gb": 160, "4Gb": 260, "8Gb": 350, "16Gb": 550, "32Gb": 850
}

# --- 2. HELPER FUNCTIONS ---
def safe_extract(match_obj, group_num=1, default="Manual Check Required"):
    """Prevents crashes when regex finds no match."""
    if match_obj:
        return match_obj.group(group_num)
    return default

def extract_data(uploaded_file):
    text = ""
    try:
        with pdfplumber.open(io.BytesIO(uploaded_file.getvalue())) as pdf:
            # Scanning more pages to ensure we catch timing tables usually in the middle
            for page in pdf.pages[:20]:
                content = page.extract_text()
                if content:
                    text += content + "\n"
    except Exception as e:
        st.error(f"Extraction Error: {e}")
    return text

def run_audit(text):
    # Aggressive patterns for Part Numbers
    pn_match = re.search(r"\b(MT40A|K4A|H5AN|IS40A|K4B|MT41|MT40)[\w\d-]+\b", text)
    
    results = {
        "PartNum": pn_match.group(0) if pn_match else "Unknown DRAM Component",
        "VDD": re.search(r"(?:VDD|Vdd)\s*[:=]?\s*([\d\.]+V)", text),
        "tAA": re.search(r"(?:tAA|Internal\sRead\sLatency|CAS\sLatency)\s*[:=]?\s*([\d\.]+ns)", text, re.IGNORECASE),
        "tRP": re.search(r"(?:tRP|Row\sPrecharge)\s*[:=]?\s*([\d\.]+ns)", text, re.IGNORECASE),
        "Density": re.search(r"(\d+\s?Gb|\d+\s?Mb)", text),
        "CRC": any(word in text.upper() for word in ["WRITE CRC", "CRC ERROR"]),
        "Parity": any(word in text.upper() for word in ["C/A PARITY", "COMMAND PARITY"])
    }
    return results

# --- 3. STREAMLIT UI ---
st.title("🛡️ Dynamic DRAM Compliance Audit")
st.markdown("### Structural validation against JEDEC JESD79-4")

uploaded_file = st.file_uploader("Upload JEDEC Datasheet (PDF)", type="pdf")

if uploaded_
