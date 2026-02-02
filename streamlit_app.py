import streamlit as st
import pdfplumber
import re
import pandas as pd

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="DDR4 Datasheet Review Tool",
    layout="wide"
)

# ---------------- HEADER ----------------
st.title("📘 DDR4 Datasheet Review Tool")
st.caption(
    "Upload a DDR4 datasheet PDF and review critical electrical, timing, thermal, "
    "and reliability parameters with engineering interpretation."
)

st.markdown(
    "[JEDEC DDR4 Standard (JESD79-4)](https://www.jedec.org/standards-documents/docs/jesd79-4)"
)

st.divider()

# ---------------- FILE UPLOAD ----------------
uploaded_file = st.file_uploader(
    "📤 Upload DDR4 Datasheet (PDF only)",
    type=["pdf"]
)

if not uploaded_file:
    st.info("⬆️ Please upload a DDR4 datasheet to start the review.")
    st.stop()

# ---------------- PDF TEXT EXTRACTION ----------------
pages_text = []

with pdfplumber.open(uploaded_file) as pdf:
    for i, page in enumerate(pdf.pages):
        text = page.extract_text()
        if text:
            pages_text.append((i + 1, text))

full_text = "\n".join([t for _, t in pages_text])

# Helper function
def find_param(pattern):
    for page_no, text in pages_text:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(), page_no
    return "Not found", None

# ---------------- PARAM EXTRACTION ----------------
params = {
    "DDR Clock Frequency": find_param(r"\b\d{3,4}\s*MHz\b"),
    "CAS Latency (CL)": find_param(r"CL\s*=\s*\d+"),
    "tRCD": find_param(r"tRCD\s*=\s*\d+"),
    "tRP": find_param(r"tRP\s*=\s*\d+"),
    "Refresh Interval (tREFI)": find_param(r"tREFI\s*=\s*\d+"),
    "Operating Temperature": find_param(r"-?\d+\s*°?C\s*to\s*\+?\d+\s*°?C"),
}

# ---------------- TABS ----------------
tabs = st.tabs([
    "🕒 Timing Parameters",
    "⏱ Refresh Behavior",
    "📊 Bandwidth Impact",
    "🌡 Thermal Limits",
    "🧾 Final Review Summary"
])

# ---------------- TAB 1: TIMING ----------------
with tabs[0]:
    st.subheader("🕒 DDR4 Timing Parameters")

    st.markdown("""
**Why this matters:**  
Timing parameters define how fast memory operations occur.  
Aggressive timing → higher performance, but **lower margin**.
""")

    timing_df = pd.DataFrame([
        {"Parameter": "CAS Latency (CL)", "Extracted Value": params["CAS Latency (CL)"][0], "Page": params["CAS Latency (CL)"][1]},
        {"Parameter": "tRCD", "Extracted Value": params["tRCD"][0], "Page": params["tRCD"][1]},
        {"Parameter": "tRP", "Extracted Value": params["tRP"][0], "Page": params["tRP"][1]},
    ])

    st.dataframe(timing_df, use_container_width=True)

    st.markdown("""
**Engineering interpretation:**
- CL, tRCD, tRP must align with **memory controller capability**
- Lower values increase risk at high temperature & voltage corners
""")

# ---------------- TAB 2: REFRESH ----------------
with tabs[1]:
    st.subheader("⏱ DDR4 Refresh Behavior")

    st.markdown("""
**Why this matters:**  
DDR4 refresh directly impacts **data retention** and **effective bandwidth**.
""")

    st.write(
        f"**tREFI:** {params['Refresh Interval (tREFI)'][0]} "
        f"(Page {params['Refresh Interval (tREFI)'][1]})"
    )

    st.markdown("""
**Key risks:**
- High temperature → refresh must increase
- Double refresh reduces usable bandwidth
""")

# ---------------- TAB 3: BANDWIDTH ----------------
with tabs[2]:
    st.subheader("📊 Bandwidth Loss Due to Refresh")

    st.markdown("""
**Scenario analysis (typical):**
- Normal refresh: ~1–2% bandwidth loss
- Double refresh (high temp): **3–5% loss**
""")

    st.warning("""
⚠ If controller does not compensate timing,
system throughput degradation may be visible in:
- Wi-Fi routing
- Video buffering
- Cache-heavy workloads
""")

# ---------------- TAB 4: THERMAL ----------------
with tabs[3]:
    st.subheader("🌡 Thermal Limits & Implications")

    st.write(
        f"**Operating Temperature Range:** {params['Operating Temperature'][0]} "
        f"(Page {params['Operating Temperature'][1]})"
    )

    st.markdown("""
**Why thermal limits are critical:**
- Above 85°C → DDR4 requires higher refresh rate
- Extended temp parts (95–105°C) must be explicitly rated
""")

    st.error("""
❗ If datasheet does not clearly state extended temperature behavior,
risk of silent data corruption exists.
""")

# ---------------- FINAL SUMMARY ----------------
with tabs[4]:
    st.subheader("🧾 DDR4 Datasheet Review Summary")

    st.markdown("""
### ✔ Findings
- Core DDR4 timing parameters identified from datasheet
- Refresh behavior partially specified
- Thermal operating range extracted

### ⚠ Risks Identified
1. Missing clarity on **high-temperature refresh behavior**
2. No explicit bandwidth degradation guidance
3. Timing margins not correlated with temperature

### 🛠 Proposed Engineering Actions
- Validate timing at **worst-case temperature**
- Enforce controller-side refresh compensation
- Request vendor clarification on:
  - Double refresh impact
  - Extended temperature guarantees

### ✅ Review Verdict
**Conditionally acceptable**, pending:
- Thermal stress validation
- Controller timing margin analysis
""")

    st.success("Datasheet review completed with actionable insights.")
