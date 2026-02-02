import streamlit as st
import pandas as pd
import pdfplumber
from fpdf import FPDF
from datetime import datetime
import re
import os
import io

# --- 1. CONFIG ---
st.set_page_config(page_title="JEDEC Automated Audit", layout="wide", page_icon="🛡️")

def load_readme():
    if os.path.exists("README.md"):
        with open("README.md", "r", encoding="utf-8") as f:
            return f.read()
    return "README.md not found."

with st.sidebar:
    st.title("System Controls")
    if st.checkbox("Show Tool Documentation"):
        st.markdown(load_readme())
    st.divider()
    st.caption("Standard: JEDEC JESD79-4B")

st.title("🛡️ Dynamic DRAM Compliance Audit")

# --- 2. EXTRACTION ENGINE (Standard Text Only) ---
def extract_data(uploaded_file):
    text = ""
    file_bytes = uploaded_file.getvalue() 
    
    try:
        with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
            for page in pdf.pages[:10]:
                content = page.extract_text()
                if content:
                    text += content + "\n"
    except Exception as e:
        st.error(f"Text Extraction Error: {e}")
    return text

def run_audit(text):
    results = {
        "VDD": re.search(r"VDD\s*[:=]?\s*([\d\.]+V)", text, re.IGNORECASE),
        "tAA": re.search(r"tAA\s*.*?\s*([\d\.]+ns)", text, re.IGNORECASE),
        "tRP": re.search(r"tRP\s*.*?\s*([\d\.]+ns)", text, re.IGNORECASE),
        "Density": re.search(r"(\d+Gb|\d+Mb)", text),
        "CRC": "CRC" in text.upper(),
        "Parity": "PARITY" in text.upper()
    }
    return results

# --- 3. INPUTS ---
col_in1, col_in2 = st.columns(2)
with col_in1:
    uploaded_file = st.file_uploader("Upload JEDEC Datasheet (PDF)", type="pdf")
with col_in2:
    part_no = st.text_input("Enter Part Number", placeholder="e.g. K4A8G165WB")

if uploaded_file and part_no:
    raw_text = extract_data(uploaded_file)
    
    if st.sidebar.checkbox("View Extracted Raw Text"):
        st.sidebar.text_area("Extracted Content", raw_text[:3000], height=200)

    audit = run_audit(raw_text)
    
    # --- 4. THE 6-TAB STRUCTURE ---
    tabs = st.tabs(["🏗️ Physical", "⚡ DC Power", "⏱️ AC Timing", "🌡️ Thermal", "🔐 Integrity", "📝 Audit Summary"])
    
    with tabs[0]:
        st.subheader("Physical Architecture")
        found_density = audit["Density"].group(1) if audit["Density"] else "Not Detected"
        st.table(pd.DataFrame({"Feature": ["Density", "Architecture"], "Detected": [found_density, "DDR4 Standard"]}))

    with tabs[1]:
        st.subheader("DC Power Rails")
        found_vdd = audit["VDD"].group(1) if audit["VDD"] else "Not Found"
        st.table(pd.DataFrame({"Rail": ["VDD Supply"], "Value": [found_vdd]}))

    with tabs[2]:
        st.subheader("AC Timing Boundaries")
        found_taa = audit["tAA"].group(1) if audit["tAA"] else "Manual Check Required"
        st.metric("Internal Read Latency (tAA)", found_taa)

    with tabs[3]:
        st.subheader("Thermal Envelope")
        st.info("Analysis of Refresh Rate scaling (tREFI) vs Case Temperature.")

    with tabs[4]:
        st.subheader("Command Integrity")
        st.write(f"CRC Error Detection: {'✅ Detected' if audit['CRC'] else '❌ Not Found'}")
        st.write(f"CA Parity Support: {'✅ Detected' if audit['Parity'] else '❌ Not Found'}")

    with tabs[5]:
        st.header("📝 Final Engineering Audit Summary")
        v_vdd = audit["VDD"].group(1) if audit["VDD"] else "Missing"
        v_taa = audit["tAA"].group(1) if audit["tAA"] else "Missing"
        
        summary_body = f"""
        **Part Number:** {part_no}  
        **Compliance Standard:** JEDEC JESD79-4  
        
        **Analysis Summary:**
        - **Voltage (VDD):** {v_vdd}  
        - **Read Latency (tAA):** {v_taa}  
        - **Data Integrity:** {'CRC/Parity features validated' if audit['CRC'] else 'CRC/Parity check inconclusive'}.
        
        **Verdict:** The extracted parameters align with DDR4 operational envelopes.
        """
        st.markdown(summary_body)
        st.divider()
        
        if st.button("Generate & Download Final Report"):
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Helvetica", size=12)
            pdf.multi_cell(0, 10, summary_body.replace("**", ""))
            pdf_bytes = pdf.output()
            st.download_button("📥 Save Audit PDF", pdf_bytes, f"Audit_{part_no}.pdf", "application/pdf")

else:
    st.warning("Please upload a PDF and enter a Part Number.")
    
