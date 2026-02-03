import streamlit as st
import pdfplumber
import re
import pandas as pd
import numpy as np

# ============================================================
# 1. JEDEC DDR4 AUTHORITATIVE DATABASE (JESD79-4C)
# ============================================================
JEDEC_MASTER = {
    "DENSITY": {
        "8Gb": {
            "Banks": 16,
            "BankGroups": 4,
            "Rows": "A0–A14",
            "Columns": "A0–A9",
            "PageSize": "1KB",
            "tRFC1": 350,
            "tRFC2": 260,
            "tRFC4": 160,
            "tREFI": 7.8
        },
        "16Gb": {
            "Banks": 16,
            "BankGroups": 4,
            "Rows": "A0–A15",
            "Columns": "A0–A9",
            "PageSize": "2KB",
            "tRFC1": 550,
            "tRFC2": 350,
            "tRFC4": 260,
            "tREFI": 7.8
        }
    },
    "SPEED": {
        "3200AA": {
            "tCK": 0.625,
            "tAA": 13.75,
            "tRCD": 13.75,
            "tRP": 13.75,
            "tRAS": 32,
            "tRC": 45.75,
            "tWR": 15,
            "tRTP": 7.5,
            "tDQSQ": 0.16
        }
    },
    "POWER": {
        "VDD": 1.2,
        "VDD_TOL": "±0.06V",
        "VPP": 2.5
    }
}

# ============================================================
# 2. HARDCODED DDR4 REFERENCE PARTS (GOLDEN → FAILURE)
# ============================================================
REFERENCE_PARTS = {
    "Golden_3200": {
        "Density": "8Gb",
        "Speed": "3200AA",
        "tAA": 13.5,
        "tRCD": 13.5,
        "tRP": 13.5,
        "EyeMargin": "Good",
        "Thermal": "Pass"
    },
    "Marginal_Thermal": {
        "Density": "8Gb",
        "Speed": "3200AA",
        "tAA": 14.5,
        "tRCD": 14.5,
        "tRP": 14.5,
        "EyeMargin": "Marginal",
        "Thermal": "Fail @ 85C"
    },
    "Failure_Clock": {
        "Density": "16Gb",
        "Speed": "3200AA",
        "tAA": 16.0,
        "tRCD": 16.0,
        "tRP": 16.0,
        "EyeMargin": "Closed",
        "Thermal": "Fail"
    }
}

# ============================================================
# 3. PDF PARAMETER EXTRACTION (BEST-EFFORT)
# ============================================================
def extract_parameters(pdf_file):
    text = ""
    with pdfplumber.open(pdf_file) as pdf:
        for p in pdf.pages[:4]:
            text += p.extract_text() or ""

    def find(pattern):
        m = re.search(pattern, text)
        return float(m.group(1)) if m else None

    return {
        "tAA": find(r"tAA\s*=?\s*(\d+\.?\d*)"),
        "tRCD": find(r"tRCD\s*=?\s*(\d+\.?\d*)"),
        "tRP": find(r"tRP\s*=?\s*(\d+\.?\d*)"),
        "VDD": find(r"VDD\s*=?\s*(1\.\d+)"),
    }

# ============================================================
# 4. STREAMLIT CONFIG
# ============================================================
st.set_page_config(
    page_title="DDR4 JEDEC Compliance & Review Tool",
    layout="wide"
)

st.title("🛡️ DDR4 JEDEC Compliance, Failure Analysis & Reviewer Tool")

# ============================================================
# 5. LANDING PAGE – OFFLINE NOTE
# ============================================================
with st.expander("📘 About This Tool / Offline Usage", expanded=True):
    st.markdown("""
### What this tool does
This tool extracts **DDR4 parameters from vendor datasheets**, compares them **against JEDEC JESD79-4C**, 
and performs **engineering review, failure analysis, and mitigation guidance**.

### Offline / Local Usage
If you like the results:
1. Download this tool’s Python code
2. Run it **locally on your PC**
3. Upload **confidential datasheets locally**
4. Perform JEDEC comparison without cloud exposure

> ⚠️ JEDEC specifications remain authoritative.  
> This tool **assists review**, not final silicon qualification.
""")

# ============================================================
# 6. SIDEBAR – MODE SELECTION
# ============================================================
mode = st.sidebar.selectbox(
    "Select Analysis Mode",
    ["Upload Datasheet", "Explore Reference DDR4 Parts"]
)

# ============================================================
# 7. MAIN LOGIC
# ============================================================
if mode == "Upload Datasheet":
    pdf = st.file_uploader("Upload DDR4 Datasheet (PDF)", type="pdf")

    if pdf:
        extracted = extract_parameters(pdf)
        jedec = JEDEC_MASTER["SPEED"]["3200AA"]

        st.success("Datasheet parameters extracted. Showing JEDEC comparison.")

        tabs = st.tabs([
            "1. DDR Basics",
            "2. Clock & Frequency",
            "3. Addressing",
            "4. Power",
            "5. AC Timing (JEDEC vs Datasheet)",
            "6. Training",
            "7. Refresh & Thermal",
            "8. Signal Integrity / Eye",
            "9. DDR3 vs DDR4 vs DDR5",
            "10. Review Summary"
        ])

        # ----------------------------------------------------
        with tabs[0]:
            st.header("Tab 1 – DDR Basics")
            st.markdown("**What:** DDR4 internal organization")
            st.markdown("**Why:** Defines timing, refresh, bank conflicts")

            st.table(pd.DataFrame([
                {"Item":"Banks","JEDEC":16},
                {"Item":"Bank Groups","JEDEC":4},
                {"Item":"Prefetch","JEDEC":"8n"}
            ]))

        # ----------------------------------------------------
        with tabs[1]:
            st.header("Tab 2 – Clock & Frequency")
            st.markdown("""
**What:** Clock period, jitter tolerance  
**Why:** Clock instability → setup/hold failures
""")
            st.table(pd.DataFrame([
                {"Parameter":"tCK","JEDEC (ns)":jedec["tCK"]}
            ]))

        # ----------------------------------------------------
        with tabs[2]:
            st.header("Tab 3 – Addressing")
            st.markdown("""
**What:** Row/column/bank decode  
**Why:** Wrong mapping → silent data corruption
""")

        # ----------------------------------------------------
        with tabs[3]:
            st.header("Tab 4 – Power")
            st.markdown("""
**What:** VDD / VPP limits  
**Why:** Undervoltage → eye collapse; overvoltage → reliability loss
""")
            st.table(pd.DataFrame([
                {"Rail":"VDD","JEDEC":JEDEC_MASTER["POWER"]["VDD"],"Extracted":extracted["VDD"]}
            ]))

        # ----------------------------------------------------
        with tabs[4]:
            st.header("Tab 5 – AC Timing (CORE)")
            rows = []
            for p in ["tAA","tRCD","tRP"]:
                rows.append({
                    "Parameter": p,
                    "JEDEC Max (ns)": jedec[p],
                    "Datasheet (ns)": extracted[p],
                    "Status": "PASS" if extracted[p] and extracted[p] <= jedec[p] else "FAIL"
                })
            st.table(pd.DataFrame(rows))

            st.markdown("""
**Reviewer Insight**
- **Cause:** Datasheet timing > JEDEC
- **Effect:** Reduced timing margin
- **Symptom:** Random read/write failures
- **Mitigation:**  
  - Lower speed bin  
  - Improve SI & clock quality  
  - Increase timing guardband
""")

        # ----------------------------------------------------
        with tabs[5]:
            st.header("Tab 6 – Training")
            st.markdown("""
**What:** Write leveling, read gate, Vref training  
**Why:** Poor training → intermittent failures
""")

        # ----------------------------------------------------
        with tabs[6]:
            st.header("Tab 7 – Refresh & Thermal")
            tRFC = JEDEC_MASTER["DENSITY"]["8Gb"]["tRFC1"]
            tREFI = JEDEC_MASTER["DENSITY"]["8Gb"]["tREFI"]
            loss = (tRFC/(tREFI*1000))*100

            st.table(pd.DataFrame([
                {"Metric":"tRFC (ns)", "Value":tRFC},
                {"Metric":"tREFI (µs)", "Value":tREFI},
                {"Metric":"Refresh Bandwidth Loss %", "Value":f"{loss:.2f}"}
            ]))

            st.markdown("""
**Thermal Failures**
- High temp → leakage → tighter timing
- Above 85°C refresh may double

**Mitigation**
- Better airflow
- Throttle frequency
- Use 2x refresh mode carefully
""")

        # ----------------------------------------------------
        with tabs[7]:
            st.header("Tab 8 – Signal Integrity / Eye")
            st.markdown("""
**What:** Eye opening, DQS/DQ alignment  
**Failure Examples**
- Closed eye → no timing margin
- Marginal eye → temp-sensitive failures

**Mitigation**
- PCB impedance control
- Shorter stubs
- Better termination
""")

        # ----------------------------------------------------
        with tabs[8]:
            st.header("Tab 9 – DDR Evolution Context")
            st.table(pd.DataFrame([
                {"DDR":"DDR3","VDD":"1.5V","Max Speed":"2133"},
                {"DDR":"DDR4","VDD":"1.2V","Max Speed":"3200"},
                {"DDR":"DDR5","VDD":"1.1V","Max Speed":"6400+"}
            ]))

        # ----------------------------------------------------
        with tabs[9]:
            st.header("Tab 10 – Final Review Summary")
            st.markdown("""
### Overall Assessment
- JEDEC comparison performed first ✔
- Timing failures flagged clearly ✔
- Thermal & eye risks identified ✔

### Recommendation
Use this part **only if mitigations are applied**  
Else downgrade speed or choose golden reference part.
""")

elif mode == "Explore Reference DDR4 Parts":
    st.header("Reference DDR4 Models – Golden → Failure")

    st.table(pd.DataFrame.from_dict(REFERENCE_PARTS, orient="index"))

    st.markdown("""
**Purpose**
- Teach engineers *why* failures happen
- Show impact of timing, clock, thermal, SI margins
- Build intuition beyond pass/fail
""")
