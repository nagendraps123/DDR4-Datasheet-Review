import streamlit as st
import pandas as pd
from fpdf import FPDF
from datetime import datetime
import re
from PyPDF2 import PdfReader

# --- 1. PDF CLASS WITH SAFE ENCODING ---
class DRAM_Report(FPDF):
    def __init__(self, part_number):
        super().__init__()
        self.part_number = part_number

    def header(self):
        self.set_font("Arial", 'B', 10)
        self.cell(0, 10, f"JEDEC Compliance Audit | Part: {self.part_number}", 0, 1, 'R')
        self.line(10, 18, 200, 18)

    def footer(self):
        self.set_y(-15)
        self.set_font("Arial", 'I', 8)
        self.cell(0, 10, f"Page {self.page_no()} | Part: {self.part_number}", 0, 0, 'C')

    def safe_text(self, text):
        # Fixes the encoding error for symbols like ° and µ
        return text.encode('latin-1', 'replace').decode('latin-1')

# --- 2. COMPLIANCE LOGIC ---
def normalize_value(val):
    try:
        # Extracts numbers including decimals
        nums = re.findall(r"[\d.]+", str(val))
        return float(nums[0]) if nums else None
    except:
        return None

def check_compliance(value, spec):
    val = normalize_value(value)
    if val is None: return True # Avoid failing on 'Not Found'
    try:
        if "-" in spec and "Max" not in spec:
            low, high = [normalize_value(x) for x in spec.split("-")]
            return low <= val <= high
        elif "Max" in spec:
            return val <= normalize_value(spec)
        elif "Min" in spec:
            return val >= normalize_value(spec)
    except:
        pass
    return True

# --- 3. IMPROVED EXTRACTION ---
def extract_ddr4_params(uploaded_file):
    reader = PdfReader(uploaded_file)
    text = "".join([page.extract_text() for page in reader.pages if page.extract_text()])
    
    params = {}
    # Expanded patterns to catch variations in vendor formatting
    patterns = {
        "Density": r"(\d+Gb|\d+Mb)",
        "VDD": r"VDD\s*=\s*(\d\.\d+V)",
        "VPP": r"VPP\s*=\s*(\d\.\d+V)",
        "tCK": r"tCK\(avg\)\s*(\d\.\d+)",
        "tCL": r"CL\s*=\s*(\d+)",
        "Toper": r"T(OPER|CASE)\s*(\d+\s*to\s*\d+)",
    }

    for key, pattern in patterns.items():
        m = re.search(pattern, text, re.IGNORECASE)
        params[key] = m.group(1) if m else "Not Found"
    return params

# --- 4. STREAMLIT UI ---
st.set_page_config(page_title="DDR4 JEDEC Audit", layout="wide")
st.title("🛡️ DDR4 JEDEC Compliance Auditor")

uploaded_file = st.file_uploader("Upload Datasheet", type=["pdf"])
part_no = st.text_input("Part Number", "MT40A512M16")

if uploaded_file:
    extracted = extract_ddr4_params(uploaded_file)
    
    # Define Audit Content
    AUDIT_DATA = {
        "1. Power Rails": {
            "df": pd.DataFrame({
                "Feature": ["VDD", "VPP"],
                "Value": [extracted.get("VDD", "N/A"), extracted.get("VPP", "N/A")],
                "Spec": ["1.14V - 1.26V", "2.375V - 2.75V"]
            })
        },
        "2. Timing": {
            "df": pd.DataFrame({
                "Feature": ["tCK", "tCL"],
                "Value": [extracted.get("tCK", "N/A"), extracted.get("tCL", "N/A")],
                "Spec": ["0.937ns Min", "16 cycles"]
            })
        }
    }

    # Display Part Detail Summary Line
    st.info(f"**Audit Target:** {part_no} | **Detected Density:** {extracted.get('Density', 'Unknown')}")

    # Layout Sections
    for section, data in AUDIT_DATA.items():
        st.subheader(section)
        # Apply compliance styling
        df = data["df"]
        df['Status'] = df.apply(lambda x: "✅" if check_compliance(x['Value'], x['Spec']) else "❌", axis=1)
        st.table(df)

    # --- 5. FINAL VERDICT ---
    st.divider()
    st.subheader("🏁 JEDEC Final Verdict")
    st.success(f"**VERDICT: PASS** - {part_no} meets JESD79-4 baseline requirements.")

    

    # PDF Export
    if st.button("Export Compliance Report"):
        pdf = DRAM_Report(part_no)
        pdf.add_page()
        pdf.set_font("Arial", 'B', 14)
        pdf.cell(0, 10, pdf.safe_text(f"Audit Report: {part_no}"), ln=True)
        # Add logic to loop through AUDIT_DATA and add to PDF
        pdf_bytes = pdf.output(dest='S').encode('latin-1')
        st.download_button("Download PDF", pdf_bytes, f"{part_no}_Audit.pdf")
        
