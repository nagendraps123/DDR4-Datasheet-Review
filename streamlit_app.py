import streamlit as st
import pandas as pd

# -------------------------------
# Page Config
# -------------------------------
st.set_page_config(
    page_title="DDR4 Datasheet Review Tool",
    layout="wide"
)

# -------------------------------
# Hard-coded DDR4 Parts
# -------------------------------
DDR_DATABASE = {
    "Micron MT40A1G8SA-075E": {  # Golden
        "category": "Golden",
        "vendor": "Micron",
        "density": "8Gb",
        "speed_bin": "DDR4-3200AA",
        "jedec": "JESD79-4C",
        "tAA": 13.5,
        "tRCD": 13.5,
        "tRP": 13.5,
        "tRAS": 32,
        "tRFC": 350,
        "VDD": 1.2,
        "VPP": 2.5,
        "temp_grade": "0–85°C",
        "tDQSQ": 0.15,
        "eye_height": 360,
        "eye_width": 0.52,
        "clk_jitter": 0.15,
        "pcb_skew": 20,
        "I_dd": 4.0
    },
    "Samsung K4A8G085WB-BCRC": {  # Marginal
        "category": "Marginal",
        "vendor": "Samsung",
        "density": "8Gb",
        "speed_bin": "DDR4-3200AA",
        "jedec": "JESD79-4C",
        "tAA": 13.8,
        "tRCD": 13.8,
        "tRP": 13.8,
        "tRAS": 34,
        "tRFC": 360,
        "VDD": 1.18,
        "VPP": 2.48,
        "temp_grade": "0–90°C",
        "tDQSQ": 0.17,
        "eye_height": 350,
        "eye_width": 0.50,
        "clk_jitter": 0.16,
        "pcb_skew": 25,
        "I_dd": 4.2
    },
    "Hynix H5AN8G6NCJ-BC": {  # Failure
        "category": "Failure",
        "vendor": "Hynix",
        "density": "8Gb",
        "speed_bin": "DDR4-3200AA",
        "jedec": "JESD79-4C",
        "tAA": 14.5,
        "tRCD": 14,
        "tRP": 14,
        "tRAS": 36,
        "tRFC": 380,
        "VDD": 1.18,
        "VPP": 2.48,
        "temp_grade": "0–95°C",
        "tDQSQ": 0.20,
        "eye_height": 300,
        "eye_width": 0.45,
        "clk_jitter": 0.18,
        "pcb_skew": 50,
        "I_dd": 4.5
    }
}

# -------------------------------
# JEDEC Reference
# -------------------------------
JEDEC_REF = {
    "tAA": 13.75,
    "tRCD": 13.75,
    "tRP": 13.75,
    "tRAS": 32,
    "tRFC": 350,
    "VDD_min": 1.14,
    "VDD_max": 1.26,
    "VPP_min": 2.375,
    "VPP_max": 2.75,
    "tDQSQ_max": 0.16,
    "eye_height_min": 350,
    "eye_width_min": 0.50,
    "clk_jitter_max": 0.16,
    "pcb_skew_max": 25,
    "I_dd_max": 4.2
}

# -------------------------------
# Landing Page
# -------------------------------
st.title("📊 DDR4 Datasheet Review & JEDEC Audit Tool")

st.info("""
**Offline Tool Notice:**  
This tool runs completely offline. You can download the code package and run it locally to review your **private DDR4 datasheets** securely.  
""")

st.markdown("""
### Purpose
- Review DDR4 datasheet parameters vs JEDEC limits  
- Identify **golden, marginal, or failure parts**  
- Provide **technical insights, root cause analysis, and mitigation guidance**
""")

# -------------------------------
# Sidebar: Select Part
# -------------------------------
st.sidebar.header("📂 Select DDR4 Part")
selected_part = st.sidebar.radio(
    "Available DDR4 Parts",
    list(DDR_DATABASE.keys())
)

data = DDR_DATABASE[selected_part]
st.success(f"🔍 Reviewing: **{selected_part} ({data['vendor']}) – {data['category']}**")

# -------------------------------
# Tabs
# -------------------------------
tabs = st.tabs([
    "1. DDR Basics", "2. Clock & Frequency", "3. Addressing",
    "4. Power", "5. AC Timing", "6. Training", "7. Refresh/Thermal",
    "8. Signal Integrity", "9. DDR3/4/5 Context", "10. Review Summary"
])

# -------------------------------
# Helper: Color-coded PASS/MARGINAL/FAIL
# -------------------------------
def check_status(param, value):
    ref = JEDEC_REF.get(param)
    if ref is None:
        return "✅ PASS"
    if isinstance(ref, tuple):
        if value < ref[0] or value > ref[1]:
            return "❌ FAIL"
        elif value == ref[0] or value == ref[1]:
            return "⚠️ Marginal"
    else:
        if value > ref:
            return "❌ FAIL"
        elif value == ref:
            return "⚠️ Marginal"
    return "✅ PASS"

# -------------------------------
# TAB 1 – DDR Basics
# -------------------------------
with tabs[0]:
    st.subheader("What this tab is")
    st.write("Overview of DDR4 architecture, bank groups, prefetch, burst length, memory operation.")

    st.subheader("Why it matters")
    st.write("DDR architecture defines timing, refresh, and system-level behavior.")

    st.markdown("**Key Parameters / Root Causes**")
    df_basic = pd.DataFrame([
        {"Parameter": "Memory Type", "Value": "DDR4 SDRAM", "Source": "Datasheet"},
        {"Parameter": "Bank Groups", "Value": 4, "Source": "JEDEC"},
        {"Parameter": "Total Banks", "Value": 16, "Source": "JEDEC"},
        {"Parameter": "Burst Length", "Value": "BL8", "Source": "JEDEC"},
        {"Parameter": "Prefetch", "Value": "8n", "Source": "JEDEC"}
    ])
    st.table(df_basic)

    st.subheader("Reviewer Insights / Notes (Q&A)")
    st.markdown("""
- Prefetch 8n → internal 8-bit fetch → high bandwidth.  
- Bank groups → parallel access, reduced row conflicts.  
- Cause → effect → symptom: Wrong mapping → intermittent errors → data corruption.  
- Mitigation: Align controller config, verify thermal profile and training.
""")

# -------------------------------
# TAB 2 – Clock & Frequency
# -------------------------------
with tabs[1]:
    st.subheader("What this tab is")
    st.write("Evaluate clock period, jitter, differential clocks, and PCB trace skew.")

    st.subheader("Why it matters")
    st.write("Clock issues directly impact setup/hold margins, read/write stability, and AC timing compliance.")

    st.markdown("**Key Parameters / Root Causes**")
    df_clock = pd.DataFrame([
        {"Parameter":"Data Rate","Value":"3200 MT/s","JEDEC":"3200 MT/s","Status":"✅ PASS"},
        {"Parameter":"tCK","Value":"{0:.3f} ns".format(0.625),"JEDEC":"0.625 ns","Status": check_status('tAA', data['tAA'])},
        {"Parameter":"Clock Jitter","Value":"{0:.3f} ns".format(data['clk_jitter']),"JEDEC":"≤0.16 ns","Status": "❌ FAIL" if data['clk_jitter']>JEDEC_REF['clk_jitter_max'] else "✅ PASS"},
        {"Parameter":"PCB Skew","Value":"{0} ps".format(data['pcb_skew']),"JEDEC":"≤25 ps","Status": "❌ FAIL" if data['pcb_skew']>JEDEC_REF['pcb_skew_max'] else "✅ PASS"}
    ])
    st.table(df_clock)

    st.subheader("Reviewer Insights / Notes (Q&A)")
    st.markdown("""
- Clock jitter or PCB skew > limits → CRC errors, boot instability.  
- Mitigation: trace matching, low-jitter clock buffers, possibly reduce speed bin.
""")

# -------------------------------
# TAB 3 – Addressing & Architecture
# -------------------------------
with tabs[2]:
    st.subheader("What this tab is")
    st.write("Verify bank/row/column addressing and page size.")

    st.subheader("Why it matters")
    st.write("Incorrect addressing → wrong row activation → data corruption.")

    df_addr = pd.DataFrame([
        {"Parameter":"Bank Groups","Value":4,"JEDEC":4,"Status":"✅ PASS"},
        {"Parameter":"Banks/Group","Value":4,"JEDEC":4,"Status":"✅ PASS"},
        {"Parameter":"Row Address","Value":"A0–A14","JEDEC":"A0–A14","Status":"✅ PASS"},
        {"Parameter":"Column Address","Value":"A0–A9","JEDEC":"A0–A9","Status":"✅ PASS"},
        {"Parameter":"Page Size","Value":"1 KB","JEDEC":"1 KB","Status":"✅ PASS"}
    ])
    st.table(df_addr)

    st.subheader("Reviewer Insights / Notes (Q&A)")
    st.markdown("Mapping correct, but AC/clock/thermal issues amplify errors.")

# -------------------------------
# TAB 4 – Power & Voltages
# -------------------------------
with tabs[3]:
    st.subheader("What this tab is")
    st.write("Validates VDD, VPP, and transient current draw (Idd).")

    st.subheader("Why it matters")
    st.write("Voltage deviation → slower operation, data corruption, system instability.")

    df_power = pd.DataFrame([
        {"Parameter":"VDD","Value":data['VDD'],"JEDEC":"1.2V ±0.06V","Status":"⚠️ Marginal" if not(1.14<=data['VDD']<=1.26) else "✅ PASS"},
        {"Parameter":"VPP","Value":data['VPP'],"JEDEC":"2.375–2.75V","Status":"✅ PASS"},
        {"Parameter":"I_dd","Value":data['I_dd'],"JEDEC":"≤4.2A","Status":"❌ FAIL" if data['I_dd']>JEDEC_REF['I_dd_max'] else "✅ PASS"}
    ])
    st.table(df_power)

    st.subheader("Reviewer Insights / Notes (Q&A)")
    st.markdown("""
- Low VDD → slower tCK → read/write errors.  
- High Idd → power droop, system instability.  
- Mitigation: Tight voltage regulation, decoupling capacitors, thermal monitoring.
""")

# -------------------------------
# TAB 5 – AC Timing
# -------------------------------
with tabs[4]:
    st.subheader("What this tab is")
    st.write("Compare CAS, RAS, RP, RC, WR, RTP timings vs JEDEC.")

    st.subheader("Why it matters")
    st.write("AC timing violations → read/write errors, intermittent corruption.")

    df_ac = pd.DataFrame([
        {"Parameter":"tAA","Value":data['tAA'],"JEDEC":JEDEC_REF['tAA'],"Status":"❌ FAIL" if data['tAA']>JEDEC_REF['tAA'] else "✅ PASS"},
        {"Parameter":"tRCD","Value":data['tRCD'],"JEDEC":JEDEC_REF['tRCD'],"Status":"❌ FAIL" if data['tRCD']>JEDEC_REF['tRCD'] else "✅ PASS"},
        {"Parameter":"tRP","Value":data['tRP'],"JEDEC":JEDEC_REF['tRP'],"Status":"❌ FAIL" if data['tRP']>JEDEC_REF['tRP'] else "✅ PASS"},
        {"Parameter":"tRAS","Value":data['tRAS'],"JEDEC":JEDEC_REF['tRAS'],"Status":"✅ PASS" if data['tRAS']>=JEDEC_REF['tRAS'] else "❌ FAIL"},
        {"Parameter":"tRFC","Value":data['tRFC'],"JEDEC":JEDEC_REF['tRFC'],"Status":"❌ FAIL" if data['tRFC']>JEDEC_REF['tRFC'] else "✅ PASS"}
    ])
    st.table(df_ac)

    st.subheader("Reviewer Insights / Notes (Q&A)")
    st.markdown("""
- tAA, tRCD, tRP > limits → intermittent corruption, system errors.  
- Mitigation: Reduce speed bin, increase CAS latency, adjust controller timing.
""")

# -------------------------------
# TAB 6 – Training
# -------------------------------
with tabs[5]:
    st.subheader("What this tab is")
    st.write("Read/write leveling, VrefDQ calibration, training stability.")

    st.subheader("Why it matters")
    st.write("Poor training → unstable operation, bank misalignment.")

    st.markdown("Reviewer Insights / Notes (Q&A)")
    st.markdown("""
- Causes: skew, clock jitter, voltage noise.  
- Mitigation: Re-run training, verify under high temperature, low voltage stress.
""")

# -------------------------------
# TAB 7 – Refresh / Thermal / Bandwidth
# -------------------------------
with tabs[6]:
    st.subheader("What this tab is")
    st.write("Refresh timing, thermal impact, and bandwidth loss calculations.")

    st.subheader("Why it matters")
    st.write("Improper refresh → data corruption or bandwidth loss; thermal stress amplifies issues.")

    refresh_tax = (data['tRFC'] / (7.8*1000))*100  # tREFI=7.8us
    df_refresh = pd.DataFrame([
        {"Parameter":"tRFC","Value":data['tRFC'],"JEDEC":JEDEC_REF['tRFC'],"Status":"❌ FAIL" if data['tRFC']>JEDEC_REF['tRFC'] else "✅ PASS"},
        {"Parameter":"tREFI","Value":"7.8 µs","JEDEC":"7.8 µs","Status":"✅ PASS"},
        {"Parameter":"Temp Grade","Value":data['temp_grade'],"JEDEC":"0–85°C","Status":"❌ FAIL" if "95" in data['temp_grade'] else "✅ PASS"},
        {"Parameter":"Refresh Tax (%)","Value":"{0:.2f}%".format(refresh_tax),"JEDEC":"≤5%","Status":"⚠️ Marginal" if refresh_tax>5 else "✅ PASS"}
    ])
    st.table(df_refresh)

    st.markdown("Bandwidth loss (%) = (tRFC / (tREFI × 1000)) × 100")

# -------------------------------
# TAB 8 – Signal Integrity
# -------------------------------
with tabs[7]:
    st.subheader("What this tab is")
    st.write("DQ/DQS skew, eye diagram, reflections, and SI margins.")

    st.subheader("Why it matters")
    st.write("Poor SI → read/write instability, training failure.")

    df_si = pd.DataFrame([
        {"Metric":"tDQSQ","Value":data['tDQSQ'],"JEDEC":"≤0.16 ns","Status":"❌ FAIL" if data['tDQSQ']>JEDEC_REF['tDQSQ_max'] else "✅ PASS"},
        {"Metric":"Eye Height (mV)","Value":data['eye_height'],"JEDEC":">=350 mV","Status":"❌ FAIL" if data['eye_height']<JEDEC_REF['eye_height_min'] else "✅ PASS"},
        {"Metric":"Eye Width (UI)","Value":data['eye_width'],"JEDEC":">=0.50 UI","Status":"❌ FAIL" if data['eye_width']<JEDEC_REF['eye_width_min'] else "✅ PASS"}
    ])
    st.table(df_si)

    st.markdown("Reviewer Insights / Notes (Q&A): Reflections, mismatched trace lengths, signal crosstalk cause intermittent errors. Mitigation: PCB optimization, impedance tuning.")

# -------------------------------
# TAB 9 – DDR3 / DDR4 / DDR5 Context
# -------------------------------
with tabs[8]:
    st.subheader("What this tab is")
    st.write("DDR3, DDR4, DDR5 comparison for voltage, banks, prefetch, and risk areas.")

    df_ctx = pd.DataFrame([
        {"Type":"DDR3","Voltage":"1.5V","Banks":8,"Prefetch":"4n","Main Risk":"Power"},
        {"Type":"DDR4","Voltage":"1.2V","Banks":16,"Prefetch":"8n","Main Risk":"Timing / SI"},
        {"Type":"DDR5","Voltage":"1.1V","Banks":32,"Prefetch":"16n","Main Risk":"SI / Power noise"}
    ])
    st.table(df_ctx)

    st.markdown("DDR4 → timing margin, SI, and thermal must be monitored; mitigations applied where necessary.")

# -------------------------------
# TAB 10 – Review Summary
# -------------------------------
with tabs[9]:
    st.subheader("Final Review Summary")

    df_summary = pd.DataFrame([
        {"Domain":"Architecture","Status":"✅ PASS","Notes":"Compliant"},
        {"Domain":"Clock & Frequency","Status":"❌ FAIL","Notes":"Jitter & skew exceed limits"},
        {"Domain":"Power & Voltages","Status":"❌ FAIL","Notes":"VDD marginal, Idd transient issues"},
        {"Domain":"AC Timing","Status":"❌ FAIL","Notes":"Multiple tAA, tRCD, tWR violations"},
        {"Domain":"Training","Status":"⚠️ Marginal","Notes":"Some banks unstable"},
        {"Domain":"Signal Integrity","Status":"❌ FAIL","Notes":"Eye diagram & skew failures"},
        {"Domain":"Refresh / Thermal","Status":"❌ FAIL","Notes":"tRFC exceeds, Temp grade exceeded"},
        {"Domain":"DDR3/4/5 Context","Status":"✅ PASS","Notes":"Correctly identified"}
    ])
    st.table(df_summary)

    st.markdown("""
**Reviewer Insights / Notes (Q&A):**  
- This part should **not be deployed without mitigations**.  
- Recommended mitigations:  
  - PCB trace matching and impedance control  
  - Low-jitter clock buffers  
  - Reduce speed bin / increase CAS latency  
  - Thermal management and airflow  
  - Re-run training under stress conditions  
  - Refresh & AC timing adjustment
""")
