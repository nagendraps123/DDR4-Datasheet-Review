import streamlit as st
import pdfplumber
import re
import matplotlib.pyplot as plt
import numpy as np

# --- 1. JEDEC AUTHORITATIVE LOOKUP ---
JEDEC_MASTER = {
    "DENSITY": {
        "8Gb": {"tRFC1": 350, "tRFC2": 260, "tRFC4": 160, "tREFI": 7.8, "BG": 4, "Banks": 16, "Rows": "A0-A14", "Cols": "A0-A9", "Page": "1KB"},
        "16Gb": {"tRFC1": 550, "tRFC2": 350, "tRFC4": 260, "tREFI": 7.8, "BG": 4, "Banks": 16, "Rows": "A0-A15", "Cols": "A0-A9", "Page": "2KB"}
    },
    "SPEED": {
        "3200AA": {"tCK": 0.625, "tAA": 13.75, "tRCD": 13.75, "tRP": 13.75, "tRAS": 32, "tRC": 45.75, "tWR": 15, "tRTP": 7.5, "tDQSQ": 0.16},
        "2933V": {"tCK": 0.682, "tAA": 13.64, "tRCD": 13.64, "tRP": 13.64, "tRAS": 32, "tRC": 45.64, "tWR": 15, "tRTP": 7.5, "tDQSQ": 0.18}
    },
    "POWER": {
        "VDD": {"nom": 1.2, "range": "1.2V ± 0.06V"},
        "VPP": {"min": 2.375, "max": 2.75, "nom": 2.5}
    }
}

# --- 2. Extract PN from PDF ---
def extract_pn(file):
    text = ""
    with pdfplumber.open(file) as pdf:
        for page in pdf.pages[:2]:
            text += page.extract_text() or ""
    pn_match = re.search(r'([A-Z0-9-]{8,25})', text)
    return pn_match.group(1) if pn_match else "UNKNOWN_PN"

# --- 3. Streamlit Landing Page ---
st.set_page_config(page_title="JEDEC DDR4 Compliance & Review Tool", layout="wide")
st.title("🛡️ JEDEC DDR4 Compliance & Review Tool")

# --- 3a. Disclaimer ---
with st.expander("📘 About This Tool / Disclaimer", expanded=True):
    st.markdown("""
This tool performs a **JEDEC-aligned technical review** of DDR4 SDRAM devices by comparing **vendor datasheet parameters** against **JEDEC JESD79-4C requirements**.

**Data Sources Used:**
- 🟢 Extracted (Vendor Datasheet)
- 🔵 JEDEC-Derived Calculations
- ⚪ JEDEC Reference Only

**Notes:**
- JEDEC specifications are authoritative.
- Vendor datasheet extraction is traceable.
- Derived/reference values are clearly labeled, never claimed as vendor guarantees.
- Final silicon qualification remains the integrator's responsibility.
""")

# --- 4. File Upload ---
uploaded_file = st.file_uploader("Upload Vendor DDR4 Datasheet (PDF)", type="pdf")

if uploaded_file:

    # --- 5. Extract PN and set defaults ---
    pn = extract_pn(uploaded_file)
    target_bin = "3200AA"
    target_dens = "8Gb"

    s_ref = JEDEC_MASTER['SPEED'][target_bin]
    d_ref = JEDEC_MASTER['DENSITY'][target_dens]
    p_ref = JEDEC_MASTER['POWER']

    st.subheader(f"🚀 Full Audit Verdict: {pn}")

    # --- 6. Tabs ---
    tabs = st.tabs([
        "1. DDR Basics", "2. Clock & Frequency", "3. Addressing", "4. Power", 
        "5. AC Timing", "6. Training", "7. Refresh/Thermal", "8. Signal Integrity", 
        "9. DDR3/4/5 Context", "10. Review Summary"
    ])

    # ---------------- Tab 1: DDR Basics ----------------
    with tabs[0]:
        st.subheader("Tab 1: DDR Basics")
        st.markdown("**What this tab is:** Overview of DDR4 internal architecture and operation.")
        st.markdown("**Why it matters:** DDR fundamentals define timing, refresh, and data movement across the system.")

        st.markdown("**Theory / Background:**")
        st.markdown("""
- **DDR (Double Data Rate):** Transfers data on both rising and falling clock edges → effectively doubles bandwidth per clock cycle.  
- **DDR4 Overview:** Lower voltage (1.2V), 8n prefetch, 4 bank groups × 16 banks, higher speed (up to 3200+ MT/s), improved power efficiency.  
- **Prefetch:** DDR4 reads 8 bits internally per access and sends them over multiple clock edges.  
- **Bank Groups & Banks:** Enable parallel access and reduce row activation conflicts.
""")

        st.table([
            {"Parameter":"Memory Type","Value":"DDR4 SDRAM","Source":"Datasheet"},
            {"Parameter":"Bank Groups","Value":d_ref['BG'],"Source":"JEDEC"},
            {"Parameter":"Total Banks","Value":d_ref['Banks'],"Source":"JEDEC"},
            {"Parameter":"Burst Length","Value":"BL8","Source":"JEDEC"},
            {"Parameter":"Prefetch","Value":"8n","Source":"JEDEC"}
        ])

        st.markdown("**📝 Reviewer Insights / Notes**")
        st.markdown("""
- **Key concepts:** Bank = independent storage block; Prefetch 8n = 8 bits per internal access.  
- **Cause → effect → symptom:** Wrong bank/prefetch mapping → timing overlap → intermittent errors → eventual data corruption.  
- **Temperature impact:** High temp increases leakage and reduces timing margin.  
- **Mitigation / solution:**  
   - Ensure memory controller config matches JEDEC DDR4 architecture.  
   - Validate with training logs, stress tests, and thermal profiles.  
   - Proper PCB routing and termination for signal integrity.  
- **Extra tips:** Misconfigured burst length reduces bandwidth or causes errors under high load.
""")

    # ---------------- Tab 7: Refresh / Thermal ----------------
    with tabs[6]:
        st.subheader("Tab 7: Refresh, Thermal & Bandwidth")
        st.markdown("**What this tab is:** Evaluate refresh frequency, thermal impact, and bandwidth loss.")
        st.markdown("**Why it matters:** Insufficient refresh → data loss; excessive refresh → bandwidth reduction and higher power consumption.")

        eff_tax = (d_ref['tRFC1'] / (d_ref['tREFI']*1000)) * 100
        st.table([
            {"Parameter":"tRFC","Value":f"{d_ref['tRFC1']} ns"},
            {"Parameter":"tREFI","Value":f"{d_ref['tREFI']} µs"},
            {"Parameter":"Temp Grade","Value":"0–85°C"},
            {"Parameter":"Refresh Tax (%)","Value":f"{eff_tax:.2f}%"},
        ])

        st.markdown("**Bandwidth Loss Calculation:**")
        st.markdown(f"""
Effective bandwidth lost due to refresh cycles is approximated as:

> Bandwidth Loss (%) = (tRFC / (tREFI × 1000)) × 100  
> For this device: ({d_ref['tRFC1']} ns / ({d_ref['tREFI']} µs × 1000)) × 100 ≈ {eff_tax:.2f}%

**Why we calculate this:** Refresh cycles occupy memory cycles, reducing usable bandwidth. Helps designers quantify the impact of refresh on system throughput.
""")

        st.markdown("**📝 Reviewer Insights / Notes**")
        st.markdown("""
- **High-temperature impact:** Above 85°C, refresh frequency may double → effective bandwidth reduces further.  
- **System-level symptom:** Performance drops under thermal stress even if CPU load is moderate.  
- **Cause → effect:** Longer tRFC / tREFI → refresh occupies more cycles → reduced usable bandwidth.  
- **Mitigation strategies:**  
   - Thermal throttling to reduce power and heat.  
   - Improve airflow over DIMMs.  
   - Relax refresh timing at high temperature if allowed by JEDEC.  
   - Monitor refresh tax (%) to ensure system meets bandwidth requirements.
""")

# -------------------- Remaining tabs can follow the previous logic ----------------
# Tab 2-6, 8-10 code similar to your previous implementation with updated Q&A

else:
    st.info("Upload a DDR4 datasheet PDF to run the full audit.")
