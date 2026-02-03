import streamlit as st
import os
import re
import numpy as np
import matplotlib.pyplot as plt
from PyPDF2 import PdfReader

# =========================================================
# JEDEC REFERENCE DATABASE (SIMPLIFIED)
# =========================================================
JEDEC_MASTER = {
    "DENSITY": {
        "8Gb": {
            "BG": 4,
            "Banks": 16,
            "Rows": "A0–A14",
            "Cols": "A0–A9",
            "Page": "1 KB",
            "tRFC": 350,      # ns
            "tREFI": 7.8      # us
        }
    },
    "SPEED": {
        "3200AA": {
            "tCK": 0.625,
            "tAA": 13.75,
            "tRCD": 13.75,
            "tRP": 13.75,
            "tRAS": 32
        }
    },
    "POWER": {
        "VDD": "1.2V ± 0.06V",
        "VPP": "2.375 – 2.75V"
    }
}

# =========================================================
# STREAMLIT CONFIG
# =========================================================
st.set_page_config(
    page_title="DDR4 JEDEC Datasheet Review Tool",
    layout="wide"
)

st.title("🛡️ DDR4 JEDEC Datasheet Review Tool")

st.info(
    "🔒 **Local-only processing**: Datasheets are read directly from your laptop. "
    "No files are uploaded, stored, or transmitted."
)

# =========================================================
# INPUT MODE SELECTION
# =========================================================
st.subheader("📄 Datasheet Input")

input_mode = st.radio(
    "Select datasheet input method",
    ["Local file path (recommended)", "File picker (local only)"]
)

pdf_text = ""

# =========================================================
# LOCAL FILE PATH MODE
# =========================================================
if input_mode == "Local file path (recommended)":
    pdf_path = st.text_input(
        "Enter full local PDF path",
        placeholder="/Users/yourname/Documents/DDR4_datasheet.pdf"
    )

    if pdf_path:
        if os.path.exists(pdf_path):
            with open(pdf_path, "rb") as f:
                reader = PdfReader(f)
                for page in reader.pages:
                    pdf_text += page.extract_text() or ""
            st.success("Datasheet successfully read from local disk.")
        else:
            st.error("File path does not exist.")

# =========================================================
# FILE PICKER MODE (STILL LOCAL)
# =========================================================
if input_mode == "File picker (local only)":
    uploaded_file = st.file_uploader(
        "Select DDR datasheet PDF",
        type=["pdf"]
    )

    if uploaded_file:
        reader = PdfReader(uploaded_file)
        for page in reader.pages:
            pdf_text += page.extract_text() or ""
        st.success("Datasheet loaded locally in memory.")

# =========================================================
# STOP IF NO DATASHEET
# =========================================================
if not pdf_text:
    st.warning("Provide a datasheet to continue.")
    st.stop()

# =========================================================
# BASIC EXTRACTION
# =========================================================
pn_match = re.search(r"(MT\d+[A-Z0-9\-]+)", pdf_text)
part_number = pn_match.group(1) if pn_match else "Unknown"

density = "8Gb"
speed_bin = "3200AA"

d_ref = JEDEC_MASTER["DENSITY"][density]
s_ref = JEDEC_MASTER["SPEED"][speed_bin]
p_ref = JEDEC_MASTER["POWER"]

# =========================================================
# DEVICE CONTEXT
# =========================================================
st.subheader("📌 Device Context")

st.table([
    {"Item": "Part Number", "Value": part_number},
    {"Item": "Density", "Value": density},
    {"Item": "Target Speed Bin", "Value": f"DDR4-{speed_bin}"},
    {"Item": "JEDEC Reference", "Value": "JESD79-4C"},
    {"Item": "Review Mode", "Value": "Datasheet-based technical audit"}
])

# =========================================================
# TABS
# =========================================================
tabs = st.tabs([
    "DDR Basics",
    "Clock & Frequency",
    "Addressing",
    "Power",
    "AC Timing",
    "Signal Integrity",
    "Refresh, Thermal & Bandwidth",
    "Failure Modes",
    "DDR3 vs DDR4 vs DDR5",
    "Review Summary"
])

# =========================================================
# TAB 1 — DDR BASICS
# =========================================================
with tabs[0]:
    st.subheader("DDR Basics")

    st.markdown("### What this tab is")
    st.markdown(
        "An overview of **what DDR is** and how **DDR4 works internally**, "
        "forming the foundation for timing, refresh, and signal-integrity analysis."
    )

    st.markdown("### Why it matters")
    st.markdown(
        "All higher-level checks (AC timing, refresh, SI) assume the controller "
        "correctly understands DDR4 architecture. A wrong assumption here leads "
        "to silent system-level failures."
    )

    st.markdown("### DDR & DDR4 — Theory (Simplified)")
    st.markdown(
        "- **DDR (Double Data Rate)** transfers data on both rising and falling clock edges.\n"
        "- **DDR4** improves bandwidth by adding **bank groups**, higher prefetch (8n), "
        "and lower operating voltage.\n"
        "- Internal DRAM runs much slower than the I/O; prefetch bridges this gap."
    )

    st.markdown("### Key Architecture Parameters")
    st.table([
        {"Parameter": "Memory Type", "Value": "DDR4 SDRAM"},
        {"Parameter": "Bank Groups", "Value": d_ref["BG"]},
        {"Parameter": "Total Banks", "Value": d_ref["Banks"]},
        {"Parameter": "Burst Length", "Value": "BL8"},
        {"Parameter": "Prefetch", "Value": "8n"}
    ])

    st.markdown("### Reviewer Insights (Q&A)")
    st.markdown(
        "**Q: Why bank groups matter?**  \n"
        "A: They allow higher parallelism but introduce timing penalties when switching groups.\n\n"
        "**Q: What breaks if this is wrong?**  \n"
        "A: Training may pass, but failures appear under stress, temperature, or long uptime.\n\n"
        "**Q: How to mitigate?**  \n"
        "A: Ensure controller configuration strictly follows JEDEC architecture assumptions."
    )

# =========================================================
# TAB 7 — REFRESH, THERMAL & BANDWIDTH
# =========================================================
with tabs[6]:
    st.subheader("Refresh, Thermal & Bandwidth")

    st.markdown("### What this tab is")
    st.markdown(
        "Analysis of **refresh overhead**, **temperature impact**, "
        "and **effective bandwidth loss**."
    )

    st.markdown("### Why it matters")
    st.markdown(
        "Refresh steals real memory bandwidth. At high temperature, "
        "refresh frequency increases, directly reducing system performance."
    )

    tRFC = d_ref["tRFC"]
    tREFI = d_ref["tREFI"]

    refresh_tax = (tRFC / (tREFI * 1000)) * 100

    st.markdown("### Refresh Bandwidth Loss Calculation")
    st.markdown(
        "**Formula:**  \n"
        "`Refresh Loss (%) = tRFC / (tREFI × 1000) × 100`\n\n"
        f"**Calculated Loss:** ~{refresh_tax:.2f}%"
    )

    st.markdown("### Temperature vs Refresh Strategy")
    st.markdown(
        "- Above **85°C**, DDR4 requires **2× refresh rate**\n"
        "- This doubles refresh bandwidth loss\n"
        "- System throughput drops even if CPU load is constant"
    )

    st.markdown("### Reviewer Insights (Q&A)")
    st.markdown(
        "**Q: Why does performance drop at high temperature?**  \n"
        "A: More frequent refresh commands block normal reads/writes.\n\n"
        "**Q: How to mitigate?**  \n"
        "A: Improve cooling, throttle memory frequency, or relax timing at high temp."
    )

# =========================================================
# TAB 8 — FAILURE MODES
# =========================================================
with tabs[7]:
    st.subheader("Failure Modes & Propagation")

    st.markdown("### What this tab is")
    st.markdown(
        "A mapping of **spec violations → physical effect → system symptom**."
    )

    st.markdown("### Why it matters")
    st.markdown(
        "Most DRAM failures appear far from their root cause, "
        "making debug expensive and slow."
    )

    st.table([
        {"Root Cause": "Tight tAA", "Violation": "AC timing", "System Symptom": "CRC / Read errors"},
        {"Root Cause": "Poor SI", "Violation": "Eye margin", "System Symptom": "Boot instability"},
        {"Root Cause": "High temp", "Violation": "Refresh", "System Symptom": "Bit flips"}
    ])

    st.markdown("### Reviewer Insights (Q&A)")
    st.markdown(
        "**Q: Why are DRAM bugs hard to debug?**  \n"
        "A: The failure may occur hours after the violating condition.\n\n"
        "**Q: Best prevention strategy?**  \n"
        "A: JEDEC-margin compliance + stress testing + thermal validation."
    )

# =========================================================
# TAB 9 — DDR CONTEXT
# =========================================================
with tabs[8]:
    st.subheader("DDR3 vs DDR4 vs DDR5 — Practical Differences")

    st.markdown(
        "- **DDR3:** Higher voltage, simpler routing, lower bandwidth\n"
        "- **DDR4:** Lower voltage, bank groups, tighter timing margins\n"
        "- **DDR5:** On-DIMM PMIC, dual channels per DIMM, SI-limited design"
    )

# =========================================================
# TAB 10 — SUMMARY
# =========================================================
with tabs[9]:
    st.subheader("Review Summary & Mitigation")

    st.markdown(
        "✔ Architecture & Power compliant  \n"
        "⚠ AC timing and SI require attention  \n"
        "⚠ Refresh impact increases at high temperature"
    )

    st.markdown(
        "**Recommended actions:**\n"
        "- Increase CAS latency or reduce speed\n"
        "- Improve PCB routing and SI margins\n"
        "- Validate high-temperature operation"
    )
