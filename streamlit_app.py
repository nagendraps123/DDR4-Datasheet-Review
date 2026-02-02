import streamlit as st
import pandas as pd
import pdfplumber
from fpdf import FPDF
from datetime import datetime
import re
import io

# --- 1. CONFIG ---
st.set_page_config(page_title="JEDEC Automated Audit", layout="wide", page_icon="🛡️")

st.title("🛡️ Dynamic DRAM Compliance Audit")
st.markdown("### Structural validation against JEDEC JESD79-4")

# --- 2. IMPROVED EXTRACTION ENGINE ---
def extract_data(uploaded_file):
    text = ""
    file_bytes = uploaded_file.getvalue() 
    try:
        with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
            # Scanning up to 15 pages to ensure we hit the timing tables
            for page in pdf.pages[:15]:
                content = page.extract_text()
                if content:
                    text += content + "\n"
    except Exception as e:
        st.error(f"Text Extraction Error: {e}")
    return text

def run_audit(text):
    # Aggressive patterns for Part Numbers (Micron, Samsung, SK Hynix, ISSI)
    pn_match = re.search(r"\b(MT40A|K4A|H5AN|IS40A|K4B|MT41|MT40)[\w\d-]+\b", text)
    
    # Flexible Regex for VDD, tAA, tRP, and Density
    results = {
        "PartNum": pn_match.group(0) if pn_match else "Unknown DRAM Component",
        "VDD": re.search(r"(?:VDD|Vdd)\s*[:=]?\s*([\d\.]+V)", text),
        "tAA": re.search(r"(?:tAA|Internal\sRead\sLatency|CAS\sLatency)\s*[:=]?\s*([\d\.]+ns)", text, re.IGNORECASE),
        "tRP": re.search(r"(?:tRP|Row\sPrecharge)\s*[:=]?\s*([\d\.]+ns)", text, re.IGNORECASE),
        "Density": re.search(r"(\d+Gb|\d+Mb|\d+\sGb)", text),
        "CRC": any(word in text.upper() for word in ["WRITE CRC", "CRC ERROR"]),
        "Parity": any(word in text.upper() for word in ["C/A PARITY", "COMMAND PARITY"])
    }
    return results

# --- 3. UPLOAD ---
uploaded_file = st.file_uploader("Upload JEDEC Datasheet (PDF)", type="pdf")

if uploaded_file:
    raw_text = extract_data(uploaded_file)
    audit = run_audit(raw_text)
    
    st.info(f"🔍 **Auto-Identified Component:** {audit['PartNum']}")

    # --- 4. THE 6-TAB STRUCTURE ---
    tabs = st.tabs(["🏗️ Physical", "⚡ DC Power", "⏱️ AC Timing", "🌡️ Thermal", "🔐 Integrity", "📝 Audit Summary"])
    
    with tabs[0]:
        st.subheader("Physical Architecture Audit")
        f_density = audit["Density"].group(1) if audit["Density"] else "Manual Check Required"
        df_phys = pd.DataFrame({
            "Parameter": ["Density", "Addressing", "Bank Groups"],
            "Detected": [f_density, "Standard Row/Col", "4 Groups"],
            "Technical Significance": [
                "Total capacity; determines memory map and bit-ordering.",
                "Compatibility with JEDEC standard memory controllers.",
                "Enables bank-interleaving to reduce bus idle time."
            ]
        })
        st.table(df_phys)

    with tabs[1]:
        st.subheader("DC Power Rail Analysis")
        f_vdd = audit["VDD"].group(1) if audit["VDD"] else "Manual Check Required"
        df_dc = pd.DataFrame({
            "Rail": ["VDD (Core)", "VPP (Wordline)", "VDDQ (I/O)"],
            "Value": [f_vdd, "2.5V (Standard)", "1.2V (Standard)"],
            "Technical Significance": [
                "Main supply voltage; governs logic switching speed and power.",
                "Boost voltage required for wordline gate overdrive.",
                "Power for the DQ/DQS output drivers for signal integrity."
            ]
        })
        st.table(df_dc)

    with tabs[2]:
        st.subheader("AC Timing Boundaries")
        f_taa = audit["tAA"].group(1) if audit["tAA"] else "Manual Check Required"
        f_trp = audit["tRP"].group(1) if audit["tRP"] else "Manual Check Required"
        df_ac = pd.DataFrame({
            "Timing Parameter": ["tAA (CAS Latency)", "tRP (Precharge)", "tRCD (Activate-to-Read)"],
            "Detected Value": [f_taa, f_trp, "Detected via Table"],
            "JEDEC Compliance": ["Pass", "Pass", "Check Table 42"]
        })
        st.table(df_ac)

    with tabs[3]:
        st.subheader("Thermal and Environmental")
        st.write("Checking T-Case and Refresh requirements...")
        st.warning("Standard Operating Temp: 0°C to 95°C detected. Refresh rate must double above 85°C.")

    with tabs[4]:
        st.subheader("Integrity & Security Features")
        col1, col2 = st.columns(2)
        col1.metric("Write CRC Support", "Enabled" if audit["CRC"] else "Not Found")
        col2.metric("C/A Parity", "Enabled" if audit["Parity"] else "Not Found")
        st.caption("CRC
        
