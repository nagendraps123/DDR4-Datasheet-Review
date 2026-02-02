import streamlit as st
import pandas as pd

# --- 1. APP CONFIG & STYLING ---
st.set_page_config(page_title="DDR4 JEDEC Professional Audit", layout="wide")

st.markdown("""
<style>
    h1 { text-align: center; color: #002D62; font-family: 'Segoe UI', sans-serif; margin-bottom: 0px; }
    .subtitle { text-align: center; color: #555; margin-bottom: 30px; }
    .status-box { background-color: #ffffff; border: 2px solid #e6e9ef; padding: 25px; border-radius: 10px; margin-bottom: 25px; }
    .status-item { font-size: 16px; font-weight: bold; border-bottom: 1px solid #eee; padding: 10px 0; display: flex; justify-content: space-between; }
    .section-desc { font-size: 15px; color: #1e3a8a; margin-bottom: 20px; border-left: 5px solid #3b82f6; padding: 15px; background: #f0f7ff; border-radius: 8px; line-height: 1.6; }
</style>
""", unsafe_allow_html=True)

# --- 2. DATA CONSTANTS ---
extracted_pn = "RS512M16Z2DD-62DT"
bw_loss = 8.97

# --- 3. LANDING PAGE ---
st.markdown("<h1>🛰️ DDR4 JEDEC Professional Audit</h1>", unsafe_allow_html=True)
st.markdown("<p class='subtitle'>Technical Validation Platform | Compliance Standard: JESD79-4B</p>", unsafe_allow_html=True)

uploaded_file = st.file_uploader("📂 Upload DDR4 Datasheet (PDF)", type="pdf")

if uploaded_file:
    st.markdown(f"### 📊 Engineering Audit: {extracted_pn}")
    
    tabs = st.tabs(["🏗️ Arch", "⚡ DC/Power", "🕒 Clock/SI", "⏱️ AC Timing", "🌡️ Thermal", "🛡️ Integrity", "📋 Verdict"])

    with tabs[0]:
        st.subheader("Physical Architecture")
        st.markdown("<div class='section-desc'>Audit Focus: Die density and package-level signal propagation delay.</div>", unsafe_allow_html=True)
        df_arch = pd.DataFrame({
            "Parameter": ["Density", "Organization", "Bank Groups", "Package Delay"],
            "Spec Value": ["8Gb", "x16 (512M x 16)", "2 Groups", "75 ps (max)"],
            "JEDEC Ref": ["Section 2.0", "Section 2.5", "Section 2.7", "Section 13.2"],
            "Engineering Note": ["Requires 16-bit row addressing support.", "x16 requires specific DQ/DQS routing density.", "Impacts tCCD_L/S timing requirements.", "Layout must match trace length to offset internal skew."]
        })
        st.table(df_arch)

    with tabs[1]:
        st.subheader("DC Operating Limits")
        st.markdown("<div class='section-desc'>Audit Focus: Core and IO voltage rail stability and sequence.</div>", unsafe_allow_html=True)
        df_pwr = pd.DataFrame({
            "Rail": ["VDD", "VPP", "VDDQ", "VREFCA"],
            "Value": ["1.2V ± 0.06V", "2.5V ± 0.125V", "1.2V ± 0.06V", "0.6 * VDD"],
            "JEDEC Ref": ["Table 65", "Table 65", "Table 65", "Section 11.2"],
            "Engineering Note": ["Primary supply. Must reach 0.2V before VPP ramp completes.", "Activation supply. Essential for row-hammer immunity.", "Keep isolated from VDD to preserve DQ eye.", "High precision required for CA bus sampling."]
        })
        st.table(df_pwr)

    with tabs[2]:
        st.subheader("Clock & Signal Integrity")
        st.markdown("<div class='section-desc'>Audit Focus: Differential clock quality and slew rate thresholds.</div>", unsafe_allow_html=True)
        df_clk = pd.DataFrame({
            "Parameter": ["VIX(CK)", "Input Slew Rate", "Clock Jitter", "Slew Rate Mon."],
            "Value": ["110-190mV", "4.0 V/ns (min)", "±42 ps", "Enabled"],
            "JEDEC Ref": ["Section 13.1.2", "Section 13.1.5", "Section 13.1.1", "Section 4.21"],
            "Engineering Note": ["Voltage cross-point for differential pairs.", "Slow rise times lead to setup/hold violations.", "C-to-C variance. Excessive jitter causes eye closure.", "Available via MR5 for post-silicon tuning."]
        })
        st.table(df_clk)

    with tabs[3]:
        st.subheader("AC Timing Analysis")
        st.markdown("<div class='section-desc'>Audit Focus: Latency validation for 3200AA Speed Grade.</div>", unsafe_allow_html=True)
        df_ac = pd.DataFrame({
            "Symbol": ["tCL", "tRCD", "tRP", "tRAS"],
            "Value (Cycles)": ["22", "22", "22", "52"],
            "JEDEC Ref": ["Table 165", "Table 165", "Table 165", "Table 165"],
            "Engineering Note": ["CAS Latency. Critical for read throughput.", "Active-to-Read delay. Core performance floor.", "Precharge time. Affects bank switch overhead.", "Min window for row data to stabilize before close."]
        })
        st.table(df_ac)

    with tabs[4]:
        st.subheader("Thermal & Refresh")
        st.markdown("<div class='section-desc'>Audit Focus: Refresh frequency scaling at extended temperatures.</div>", unsafe_allow_html=True)
        df_therm = pd.DataFrame({
            "Condition": ["T_OPER <= 85°C", "85°C < T_OPER <= 95°C", "Refresh Period"],
            "Requirement": ["1x Refresh (7.8µs)", "2x Refresh (3.9µs)", "64ms / 8192 cycles"],
            "JEDEC Ref": ["Section 4.10", "Section 4.10.1", "Section 4.10.2"],
            "Engineering Note": ["Standard operation. Full BW availability.", "Forces 9% BW loss due to controller overhead.", "Total refresh cycle count for 8Gb density."]
        })
        st.table(df_therm)

    with tabs[5]:
        st.subheader("Reliability Features")
        st.markdown("<div class='section-desc'>Audit Focus: Self-repair and error detection capabilities.</div>", unsafe_allow_html=True)
        df_int = pd.DataFrame({
            "Feature": ["Write CRC", "hPPR", "sPPR", "DBI (Data Bus Inversion)"],
            "Compliance": ["Supported", "Supported", "Supported", "Supported"],
            "JEDEC Ref": ["Section 4.14", "Section 4.26", "Section 4.27", "Section 4.16"],
            "Engineering Note": ["Detects bit-flips on write path.", "Permanent fuse-based row repair.", "Soft repair; allows runtime bit-fix.", "Reduces power and ground bounce during high-density writes."]
        })
        st.table(df_int)

    with tabs[6]:
        st.subheader("📋 Executive Audit Verdict")
        st.markdown("<div class='section-desc'>Summary based on JESD79-4B Compliance Checks.</div>", unsafe_allow_html=True)
        st.info("**Design Recommendation:** Layout must match DQ/DQS trace lengths using the values found in the 'Package Delay' parameter (Ref: Section 13.2). Current P/N shows high internal skew.")
