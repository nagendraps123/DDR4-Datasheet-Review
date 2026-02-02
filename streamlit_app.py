import streamlit as st
import pandas as pd
import pdfplumber
from fpdf import FPDF
from datetime import datetime
import re
import io

# --- 1. CONFIG & CONSTANTS ---
st.set_page_config(page_title="JEDEC Automated Audit", layout="wide", page_icon="🛡️")

TRFC_MAP = {
    "2Gb": 160, "4Gb": 260, "8Gb": 350, "16Gb": 550, "32Gb": 850
}

# --- 2. EXTRACTION ENGINE ---
def extract_data(uploaded_file):
    text = ""
    try:
        with pdfplumber.open(io.BytesIO(uploaded_file.getvalue())) as pdf:
            for page in pdf.pages[:15]:
                content = page.extract_text()
                if content:
                    text += content + "\n"
    except Exception as e:
        st.error(f"Text Extraction Error: {e}")
    return text

def run_audit(text):
    # Improved patterns to prevent "None" results
    pn_match = re.search(r"\b(MT40A|K4A|H5AN|IS40A|K4B|MT41|MT40)[\w\d-]+\b", text)
    density_match = re.search(r"(\d+\s?Gb|\d+\s?Mb)", text)
    
    results = {
        "PartNum": pn_match.group(0) if pn_match else "Generic DRAM Component",
        "VDD": re.search(r"(?:VDD|Vdd)\s*[:=]?\s*([\d\.]+V)", text),
        "tAA": re.search(r"(?:tAA|CAS\sLatency)\s*[:=]?\s*([\d\.]+ns)", text, re.IGNORECASE),
        "tRP": re.search(r"(?:tRP|Row\sPrecharge)\s*[:=]?\s*([\d\.]+ns)", text, re.IGNORECASE),
        "Density": density_match.group(0).replace(" ", "") if density_match else "8Gb",
        "CRC": any(word in text.upper() for word in ["WRITE CRC", "CRC ERROR"]),
        "Parity": any(word in text.upper() for word in ["C/A PARITY", "COMMAND PARITY"])
    }
    return results

# --- 3. UI LAYOUT ---
st.title("🛡️ Dynamic DRAM Compliance Audit")

uploaded_file = st.file_uploader("Upload JEDEC Datasheet (PDF)", type="pdf")

if uploaded_file:
    raw_text = extract_data(uploaded_file)
    
    # DEBUG OPTION: Check if text is actually being read
    with st.expander("🛠️ Debug: View Raw Extracted Text"):
        if raw_text:
            st.text(raw_text[:2000] + "...") # Show first 2000 chars
        else:
            st.error("No text could be extracted. The PDF might be an image/scan.")

    audit = run_audit(raw_text)
    st.info(f"🔍 **Auto-Identified:** {audit['PartNum']}")

    tabs = st.tabs(["🏗️ Physical", "⚡ DC Power", "⏱️ AC Timing", "🌡️ Thermal", "🔐 Integrity", "📝 Summary"])
    
    with tabs[0]:
        st.subheader("Physical Architecture")
        st.table(pd.DataFrame({
            "Parameter": ["Density", "Addressing"],
            "Detected": [audit["Density"], "Standard JEDEC"]
        }))

    with tabs[1]:
        st.subheader("DC Rail Analysis")
        vdd_val = audit["VDD"].group(1) if audit["VDD"] else "1.2V (Assumed)"
        st.metric("Detected VDD", vdd_val)

    with tabs[2]:
        st.subheader("AC Timing")
        taa = audit["tAA"].group(1) if audit["tAA"] else "Check Table 42"
        trp = audit["tRP"].group(1) if audit["tRP"] else "Check Table 42"
        st.write(f"**CAS Latency (tAA):** {taa}")
        st.write(f"**Precharge (tRP):** {trp}")

    with tabs[3]:
        st.subheader("Thermal & Refresh")
        # Logic for Refresh Interval
        d_val = int(re.search(r'\d+', audit["Density"]).group())
        tREFI = 7.8 if d_val <= 16 else 3.9
        tRFC = TRFC_MAP.get(audit["Density"], 350)
        
        c1, c2, c3 = st.columns(3)
        c1.metric("tREFI (Norm)", f"{tREFI} µs")
        c2.metric("tREFI (Ext)", f"{tREFI/2} µs")
        c3.metric("tRFC (Min)", f"{tRFC} ns")
        
        

    with tabs[4]:
        st.subheader("Integrity Features")
        st.write(f"**Write CRC:** {'✅ Found' if audit['CRC'] else '❌ Not Found'}")
        st.write(f"**C/A Parity:** {'✅ Found' if audit['Parity'] else '❌ Not Found'}")

    with tabs[5]:
        st.subheader("Audit Summary")
        score = sum([20 for k in ["VDD", "tAA", "tRP"] if audit[k]])
        score += 20 if audit["CRC"] else 0
        score += 20 if audit["Parity"] else 0
        st.header(f"Compliance Score: {score}%")
        st.progress(score / 100)
        
