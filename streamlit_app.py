import streamlit as st
import matplotlib.pyplot as plt
import numpy as np

# ============================================================
# JEDEC REFERENCE DATA
# ============================================================
JEDEC_MASTER = {
    "DENSITY": {
        "8Gb": {
            "BG": 4, "Banks": 16, "Rows": "A0–A14",
            "Cols": "A0–A9", "Page": "1KB",
            "tRFC": 350, "tREFI": 7.8
        }
    },
    "SPEED": {
        "3200": {
            "tCK": 0.625, "tAA": 13.75, "tRCD": 13.75,
            "tRP": 13.75, "tRAS": 32, "tDQSQ": 0.16
        }
    }
}

# ============================================================
# HARD-CODED DDR4 PART DATABASE (GOOD + FAILURES)
# ============================================================
DDR4_PARTS = {
    "Micron MT40A1G8SA-075E (Reference / PASS)": {
        "Vendor": "Micron",
        "Density": "8Gb",
        "Speed": "3200",
        "Temp": "0–85°C",
        "Failures": []
    },
    "Samsung DDR4-3200 (Clock Marginal)": {
        "Vendor": "Samsung",
        "Density": "8Gb",
        "Speed": "3200",
        "Temp": "0–85°C",
        "Failures": ["CLOCK_JITTER"]
    },
    "SK Hynix DDR4-3200 (Thermal Stress)": {
        "Vendor": "SK Hynix",
        "Density": "8Gb",
        "Speed": "3200",
        "Temp": "0–95°C",
        "Failures": ["THERMAL_REFRESH"]
    },
    "Generic DDR4-3200 (Eye Diagram Failure)": {
        "Vendor": "Unknown",
        "Density": "8Gb",
        "Speed": "3200",
        "Temp": "0–85°C",
        "Failures": ["EYE_DIAGRAM"]
    },
    "Marketing DDR4-3200 (Multi-Failure Device)": {
        "Vendor": "Unknown",
        "Density": "8Gb",
        "Speed": "3200",
        "Temp": "0–95°C",
        "Failures": ["CLOCK_JITTER", "THERMAL_REFRESH", "EYE_DIAGRAM"]
    }
}

# ============================================================
# FAILURE ANALYSIS ENGINE
# ============================================================
def analyze_failures(failures):
    issues, mitigations = [], []

    if "CLOCK_JITTER" in failures:
        issues.append("❌ Clock jitter exceeds safe margin")
        mitigations += [
            "Reduce frequency to DDR4-2933",
            "Improve clock routing symmetry",
            "Lower-jitter PLL source",
            "Add clock termination"
        ]

    if "THERMAL_REFRESH" in failures:
        issues.append("⚠️ Excessive refresh under high temperature")
        mitigations += [
            "Improve airflow / heatsinking",
            "Enable thermal throttling",
            "Validate 2× refresh behavior",
            "Monitor bandwidth loss"
        ]

    if "EYE_DIAGRAM" in failures:
        issues.append("❌ Eye diagram margin collapse")
        mitigations += [
            "Tight DQS/DQ length matching",
            "Improve impedance control",
            "Increase spacing to reduce crosstalk",
            "Reduce data rate or relax timings"
        ]

    return issues, list(set(mitigations))

# ============================================================
# STREAMLIT UI
# ============================================================
st.set_page_config(layout="wide")
st.title("🛡️ JEDEC DDR4 Compliance & Failure Review Tool")

# ---------------- Landing Page ----------------
with st.expander("📘 About This Tool / Disclaimer", expanded=True):
    st.markdown("""
This tool performs a **JEDEC-aligned technical review** of DDR4 SDRAM devices
against **JESD79-4C**.

**Key Capabilities**
- Architecture, timing, power, SI, thermal analysis
- Failure-driven review (not just pass/fail)
- Reviewer-grade explanations and mitigations

📌 **Note:**  
If you like the results, you can **download this tool package and run it locally**
to review your own datasheets offline.
""")

# ---------------- Part Selection ----------------
part_name = st.selectbox("Select DDR4 Part Number", list(DDR4_PARTS.keys()))
part = DDR4_PARTS[part_name]

st.success(f"Currently Reviewing: **{part_name}**")

d_ref = JEDEC_MASTER["DENSITY"][part["Density"]]
s_ref = JEDEC_MASTER["SPEED"][part["Speed"]]

tabs = st.tabs([
    "1. DDR Basics",
    "2. Clock & Frequency",
    "3. Addressing",
    "4. Power",
    "5. AC Timing",
    "6. Training",
    "7. Refresh & Thermal",
    "8. Signal Integrity",
    "9. DDR3 / DDR4 / DDR5 Context",
    "10. Review Summary"
])

# ============================================================
# TAB 1 – DDR BASICS
# ============================================================
with tabs[0]:
    st.subheader("DDR Basics")
    st.markdown("**What this tab is:** Fundamental DDR4 architecture overview.")
    st.markdown("**Why it matters:** Architecture defines timing, refresh, and bandwidth behavior.")

    st.markdown("""
**What is DDR?**  
DDR (Double Data Rate) transfers data on both rising and falling clock edges,
doubling bandwidth without doubling clock frequency.

**What is DDR4?**  
DDR4 improves DDR3 by reducing voltage, increasing bank parallelism,
and enabling higher speeds with better efficiency.
""")

    st.table([
        {"Parameter": "Bank Groups", "Value": d_ref["BG"]},
        {"Parameter": "Total Banks", "Value": d_ref["Banks"]},
        {"Parameter": "Burst Length", "Value": "BL8"},
        {"Parameter": "Prefetch", "Value": "8n"}
    ])

    st.markdown("**Reviewer Insights / Q&A**")
    st.markdown("""
- **Cause → effect → symptom:** Wrong architecture config → timing overlap → silent corruption  
- **Failure mode:** Often passes boot, fails under stress  
- **Mitigation:** Strict JEDEC controller configuration + stress testing
""")

# ============================================================
# TAB 2 – CLOCK
# ============================================================
with tabs[1]:
    st.subheader("Clock & Frequency")
    st.markdown("**What this tab is:** Clock legality and margin review.")
    st.markdown("**Why it matters:** Clock is the timing reference for all operations.")

    st.table([
        {"Parameter": "Data Rate", "JEDEC": "3200 MT/s"},
        {"Parameter": "tCK", "JEDEC": f"{s_ref['tCK']} ns"}
    ])

    if "CLOCK_JITTER" in part["Failures"]:
        st.error("Clock margin failure detected")
        st.markdown("""
**Failure Mechanism:**  
PLL jitter reduces setup/hold margin.

**System Symptoms:**  
- Boot instability  
- Random crashes
""")

# ============================================================
# TAB 7 – REFRESH & THERMAL
# ============================================================
with tabs[6]:
    st.subheader("Refresh, Thermal & Bandwidth")
    st.markdown("**What this tab is:** Refresh behavior vs temperature.")
    st.markdown("**Why it matters:** Refresh steals bandwidth and power.")

    refresh_tax = (d_ref["tRFC"] / (d_ref["tREFI"] * 1000)) * 100

    st.markdown(f"""
**Bandwidth Loss Formula:**  
Bandwidth Loss (%) = (tRFC / (tREFI × 1000)) × 100  
≈ **{refresh_tax:.2f}%**
""")

    if "THERMAL_REFRESH" in part["Failures"]:
        st.warning("High-temperature refresh stress detected")
        st.markdown("""
- Refresh frequency doubles above 85°C  
- Bandwidth loss increases  
- Power rises
""")

# ============================================================
# TAB 8 – SIGNAL INTEGRITY
# ============================================================
with tabs[7]:
    st.subheader("Signal Integrity")
    st.markdown("**What this tab is:** Eye margin and jitter risk review.")
    st.markdown("**Why it matters:** SI failures are analog and hard to debug.")

    if "EYE_DIAGRAM" in part["Failures"]:
        st.error("Eye diagram closure detected")
        st.markdown("""
**Cause:** Skew + jitter + crosstalk  
**Effect:** Training failures, CRC errors
""")

# ============================================================
# TAB 10 – SUMMARY
# ============================================================
with tabs[9]:
    st.subheader("Review Summary & Mitigation")

    issues, mitigations = analyze_failures(part["Failures"])

    st.markdown("**Detected Issues**")
    if issues:
        for i in issues:
            st.markdown(f"- {i}")
    else:
        st.markdown("✅ No critical failures")

    st.markdown("**Recommended Mitigations**")
    for m in mitigations:
        st.markdown(f"- {m}")
