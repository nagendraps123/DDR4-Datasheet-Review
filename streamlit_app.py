import streamlit as st
import pandas as pd
import io
import re

# --- 1. JEDEC CONSTANTS & DATABASE ---
JEDEC_DB = {
    "3200AA": {"tAA": 13.75, "tRCD": 13.75, "tRP": 13.75, "tCK": 0.625, "CL": 22},
    "3200AC": {"tAA": 15.00, "tRCD": 15.00, "tRP": 15.00, "tCK": 0.625, "CL": 24},
    "2933V":  {"tAA": 13.64, "tRCD": 13.64, "tRP": 13.64, "tCK": 0.682, "CL": 20},
    "2666T":  {"tAA": 13.50, "tRCD": 13.50, "tRP": 13.50, "tCK": 0.750, "CL": 18},
}

REFRESH_DB = {
    "8Gb": {"tRFC": 350, "tREFI": 7.8},
    "16Gb": {"tRFC": 550, "tREFI": 7.8},
}

# --- 2. CORE LOGIC FUNCTIONS ---
def audit_logic(vendor_val, jedec_val, direction="max"):
    if direction == "max":
        status = "✅ Pass" if vendor_val <= jedec_val else "🚨 FAIL"
    else:
        status = "✅ Pass" if vendor_val >= jedec_val else "🚨 FAIL"
    return status

def calculate_refresh_tax(trfc, trefi):
    # tREFI is in us, tRFC is in ns. Convert to same unit.
    tax = (trfc / (trefi * 1000)) * 100
    return round(tax, 2)

# --- 3. STREAMLIT UI ---
st.set_page_config(page_title="DDR4 JEDEC Silicon-Audit", layout="wide")

st.title("🛠️ DDR4 Silicon-Audit & JEDEC Comparator")
st.markdown("### Technical Gatekeeper: JESD79-4B Compliance Verification")

# Sidebar for Inputs
st.sidebar.header("📂 Data Ingestion")
uploaded_file = st.sidebar.file_uploader("Upload Vendor Datasheet (PDF)", type="pdf")
target_bin = st.sidebar.selectbox("Target Speed Bin", list(JEDEC_DB.keys()))
density = st.sidebar.selectbox("Silicon Density", ["8Gb", "16Gb"])

if uploaded_file:
    # SIMULATED EXTRACTION (In real GitHub code, use PyMuPDF or pdfplumber here)
    # Mocking extracted data for demonstration
    vendor_data = {
        "pn": "MT40A1G8-062E",
        "tAA": 14.06,  # Slower than 13.75
        "tRCD": 13.75,
        "tRP": 13.75,
        "tRFC": 350,
        "v_dd": 1.2,
        "bg_count": 4,
        "page_proof": 18
    }

    # --- EXECUTIVE SUMMARY ---
    tax = calculate_refresh_tax(vendor_data['tRFC'], REFRESH_DB[density]['tREFI'])
    
    st.subheader("🚀 Executive Audit Summary")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Part Number", vendor_data['pn'])
    col2.metric("Detected Density", density)
    col3.metric("Refresh Tax", f"{tax}%", delta="- High Performance" if tax > 5 else "Normal")
    
    verdict = "🚨 CONDITIONAL FAIL" if vendor_data['tAA'] > JEDEC_DB[target_bin]['tAA'] else "✅ PASS"
    col4.subheader(f"Verdict: {verdict}")

    # --- 9 TAB INTERFACE ---
    tabs = st.tabs([
        "0. Basics", "1. Addressing", "2. Power", "3. AC Timings", 
        "4. Refresh", "5. Initialization", "6. DQ/SI", "7. Thermal", "8. Validation Log"
    ])

    # TAB 0: BASICS
    with tabs[0]:
        st.markdown("### DDR4 Architecture Fundamentals")
        st.write("DDR4 introduces Bank Groups to increase bandwidth. Understanding the relationship between the clock and data strobe is key to auditing this datasheet.")
        

    # TAB 1: ADDRESSING
    with tabs[1]:
        st.write("### Configuration & Addressing Audit")
        df1 = pd.DataFrame([{
            "Parameter": "Bank Groups",
            "Vendor": vendor_data['bg_count'],
            "JEDEC": 4,
            "Status": "✅ Pass",
            "Ref": "Table 2",
            "Note": "Correct BG count for x8 organization."
        }])
        st.table(df1)
        

    # TAB 3: AC TIMINGS (THE BRAIN)
    with tabs[3]:
        st.write("### Speed Bin Authentication")
        status_taa = audit_logic(vendor_data['tAA'], JEDEC_DB[target_bin]['tAA'])
        df3 = pd.DataFrame([
            {"Parameter": "tAA (ns)", "Vendor": vendor_data['tAA'], "JEDEC": JEDEC_DB[target_bin]['tAA'], "Status": status_taa, "Ref": "Table 136"},
            {"Parameter": "tRCD (ns)", "Vendor": vendor_data['tRCD'], "JEDEC": JEDEC_DB[target_bin]['tRCD'], "Status": "✅ Pass", "Ref": "Table 136"}
        ])
        st.table(df3)
        if status_taa == "🚨 FAIL":
            st.error(f"**Warning:** Vendor tAA exceeds JEDEC limit for {target_bin}. This chip is effectively a slower grade (3200AC).")
        

    # TAB 8: VALIDATION LOG
    with tabs[8]:
        st.write("### 🔍 Traceability & Validation Proof")
        log_data = [
            {"Parameter": "AC Timings", "Source": f"Page {vendor_data['page_proof']}", "Snippet": "tAA (min) ... 14.06ns", "Method": "Regex Search"},
            {"Parameter": "Power Rails", "Source": "Page 5", "Snippet": "VDD = 1.2V +/- 0.06V", "Method": "Table Extraction"}
        ]
        st.table(log_data)

    # --- EXPORT TO EXCEL (io.BytesIO) ---
    st.divider()
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
        df3.to_excel(writer, sheet_name='AC_Timings_Audit')
        # Add all other tab dataframes here
    
    st.download_button(
        label="📥 Download Professional Audit Report (Excel)",
        data=buffer.getvalue(),
        file_name=f"JEDEC_Audit_{vendor_data['pn']}.xlsx",
        mime="application/vnd.ms-excel"
    )

else:
    st.info("Please upload a DDR4 datasheet PDF to begin the automated audit.")
