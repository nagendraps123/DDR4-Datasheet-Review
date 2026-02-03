import streamlit as st
import pandas as pd
import numpy as np

# =========================================================
# JEDEC DDR4 MASTER (AUTHORITATIVE – JESD79-4C)
# =========================================================
JEDEC = {
    "Density": {
        "8Gb": {"Banks": 16, "BG": 4, "Rows": "A0–A14", "Cols": "A0–A9", "tRFC": 350, "tREFI": 7.8},
        "16Gb": {"Banks": 16, "BG": 4, "Rows": "A0–A15", "Cols": "A0–A9", "tRFC": 550, "tREFI": 7.8},
    },
    "Speed_3200": {
        "tCK": 0.625,
        "tAA": 13.75,
        "tRCD": 13.75,
        "tRP": 13.75,
        "tRAS": 32,
        "tRC": 45.75,
        "tWR": 15,
        "tRTP": 7.5,
        "tDQSQ": 0.16
    },
    "Power": {"VDD": 1.2, "VDD_tol": "±0.06V", "VPP": 2.5}
}

# =========================================================
# HARD-CODED DDR4 PART MODELS (Golden → Failure)
# =========================================================
PARTS = {
    "Golden_8Gb_3200": {
        "Density": "8Gb",
        "tAA": 13.5,
        "tRCD": 13.5,
        "tRP": 13.5,
        "Clock_Jitter_ps": 25,
        "Eye_Margin": "Wide",
        "Thermal": "Pass @ 85C"
    },
    "Marginal_Thermal": {
        "Density": "8Gb",
        "tAA": 14.6,
        "tRCD": 14.6,
        "tRP": 14.6,
        "Clock_Jitter_ps": 45,
        "Eye_Margin": "Marginal",
        "Thermal": "Fail > 80C"
    },
    "Failure_Clock_Eye": {
        "Density": "16Gb",
        "tAA": 16.0,
        "tRCD": 16.0,
        "tRP": 16.0,
        "Clock_Jitter_ps": 70,
        "Eye_Margin": "Closed",
        "Thermal": "Fail"
    }
}

# =========================================================
# STREAMLIT SETUP
# =========================================================
st.set_page_config("DDR4 JEDEC Review Tool", layout="wide")
st.title("🛡️ DDR4 JEDEC Compliance, Failure & Review Tool")

# =========================================================
# LANDING PAGE / OFFLINE NOTE
# =========================================================
with st.expander("📘 About this tool / Offline usage", expanded=True):
    st.markdown("""
### Purpose
This tool **does NOT depend on datasheet upload**.

It teaches and reviews:
- JEDEC DDR4 requirements
- How real parts compare
- Why marginal and failing parts break
- What mitigations actually work

### Offline usage
You can:
1. Download this Python tool
2. Run it locally
3. Modify / add part models
4. Later connect your **own internal datasheet extraction**

No cloud dependency required.
""")

# =========================================================
# PART SELECTION
# =========================================================
part_name = st.sidebar.selectbox("Select DDR4 Part Model", list(PARTS.keys()))
part = PARTS[part_name]
jedec_speed = JEDEC["Speed_3200"]
jedec_density = JEDEC["Density"][part["Density"]]

# =========================================================
# TABS (ALL 10 – NO MISSING)
# =========================================================
tabs = st.tabs([
    "1. DDR Basics",
    "2. Clock & Frequency",
    "3. Addressing",
    "4. Power",
    "5. AC Timing (JEDEC vs Part)",
    "6. Training",
    "7. Refresh & Thermal",
    "8. Signal Integrity / Eye",
    "9. DDR3 vs DDR4 vs DDR5",
    "10. Final Review Summary"
])

# ---------------------------------------------------------
with tabs[0]:
    st.header("Tab 1 – DDR Basics")
    st.markdown("""
**What:** DDR4 architecture (banks, bank groups, prefetch)  
**Why:** Defines parallelism, refresh behavior, timing constraints
""")
    st.table(pd.DataFrame([
        {"Parameter": "Banks", "JEDEC": jedec_density["Banks"]},
        {"Parameter": "Bank Groups", "JEDEC": jedec_density["BG"]},
        {"Parameter": "Prefetch", "JEDEC": "8n"}
    ]))

    st.markdown("""
**Reviewer Insight**
- Wrong bank-group usage → tCCD_L violations  
- Symptoms: random bandwidth drops, stalls  
- Mitigation: controller BG-aware scheduling
""")

# ---------------------------------------------------------
with tabs[1]:
    st.header("Tab 2 – Clock & Frequency")
    st.markdown("""
**What:** Clock period, jitter tolerance  
**Why:** DDR is edge-sensitive; jitter eats setup/hold margin
""")
    st.table(pd.DataFrame([
        {"Item": "tCK (ns)", "JEDEC": jedec_speed["tCK"]},
        {"Item": "Clock Jitter (ps)", "Part": part["Clock_Jitter_ps"]}
    ]))

    st.markdown("""
**Failure mode**
- High jitter → read capture errors  
**Mitigation**
- Better PLL
- Shorter clock routes
""")

# ---------------------------------------------------------
with tabs[2]:
    st.header("Tab 3 – Addressing")
    st.markdown("""
**What:** Row / Column / Bank decoding  
**Why:** Address errors are silent but fatal
""")
    st.table(pd.DataFrame([
        {"Rows": jedec_density["Rows"], "Columns": jedec_density["Cols"]}
    ]))

# ---------------------------------------------------------
with tabs[3]:
    st.header("Tab 4 – Power")
    st.markdown("""
**What:** VDD / VPP limits  
**Why:** Voltage directly affects eye opening
""")
    st.table(pd.DataFrame([
        {"Rail": "VDD", "JEDEC": JEDEC["Power"]["VDD"], "Tolerance": JEDEC["Power"]["VDD_tol"]},
        {"Rail": "VPP", "JEDEC": JEDEC["Power"]["VPP"]}
    ]))

# ---------------------------------------------------------
with tabs[4]:
    st.header("Tab 5 – AC Timing (CORE)")
    rows = []
    for p in ["tAA", "tRCD", "tRP"]:
        rows.append({
            "Parameter": p,
            "JEDEC Max (ns)": jedec_speed[p],
            "Part (ns)": part[p],
            "Result": "PASS" if part[p] <= jedec_speed[p] else "FAIL"
        })
    st.table(pd.DataFrame(rows))

    st.markdown("""
**Cause → Effect → Symptom**
- Timing > JEDEC → margin loss  
- Symptom: failures only at temp / voltage corners  
**Mitigation**
- Lower speed bin
- Add guardband
""")

# ---------------------------------------------------------
with tabs[5]:
    st.header("Tab 6 – Training")
    st.markdown("""
**What:** Write leveling, read gate, Vref training  
**Why:** DDR4 cannot work without training
""")
    st.markdown("""
**Failures**
- Poor training convergence  
- Temperature drift invalidates training  
**Mitigation**
- Periodic retraining
- Per-rank calibration
""")

# ---------------------------------------------------------
with tabs[6]:
    st.header("Tab 7 – Refresh & Thermal")
    refresh_loss = (jedec_density["tRFC"] / (jedec_density["tREFI"] * 1000)) * 100
    st.table(pd.DataFrame([
        {"Metric": "tRFC (ns)", "Value": jedec_density["tRFC"]},
        {"Metric": "Refresh BW Loss %", "Value": f"{refresh_loss:.2f}%"},
        {"Metric": "Thermal Status", "Value": part["Thermal"]}
    ]))

    st.markdown("""
**Failure**
- High temp → more refresh → bandwidth collapse  
**Mitigation**
- Airflow
- Throttling
""")

# ---------------------------------------------------------
with tabs[7]:
    st.header("Tab 8 – Signal Integrity / Eye")
    st.table(pd.DataFrame([
        {"Eye Margin": part["Eye_Margin"]}
    ]))

    st.markdown("""
**Eye failures**
- Closed eye → no timing margin  
- Marginal eye → temp-sensitive crashes  
**Mitigation**
- Impedance control
- Shorter stubs
""")

# ---------------------------------------------------------
with tabs[8]:
    st.header("Tab 9 – DDR Evolution")
    st.table(pd.DataFrame([
        {"DDR": "DDR3", "VDD": "1.5V", "Max Speed": "2133"},
        {"DDR": "DDR4", "VDD": "1.2V", "Max Speed": "3200"},
        {"DDR": "DDR5", "VDD": "1.1V", "Max Speed": "6400+"}
    ]))

# ---------------------------------------------------------
with tabs[9]:
    st.header("Tab 10 – Final Review Summary")
    st.markdown(f"""
### Part reviewed: **{part_name}**

**Verdict**
- JEDEC timing: {'PASS' if part['tAA'] <= jedec_speed['tAA'] else 'FAIL'}
- Clock robustness: {'PASS' if part['Clock_Jitter_ps'] < 50 else 'FAIL'}
- Thermal margin: {part['Thermal']}

### Recommendation
- Golden → production ready  
- Marginal → use with mitigation  
- Failure → do not release
""")
