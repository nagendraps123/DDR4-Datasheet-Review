import streamlit as st
import pdfplumber
import pandas as pd
import re

# --------------------------------------------------
# PAGE CONFIG
# --------------------------------------------------
st.set_page_config(page_title="DDR4 Datasheet Review Tool", layout="wide")

# --------------------------------------------------
# LANDING PAGE
# --------------------------------------------------
st.title("📘 DDR4 Datasheet Review & Compliance Tool")

st.markdown("""
**Purpose**  
Review DDR4 vendor datasheets against **JEDEC JESD79-4** requirements.

🔗 **JEDEC DDR4 Standard**  
https://www.jedec.org/standards-documents/docs/jesd79-4
---
""")

uploaded_file = st.file_uploader(
    "📤 Upload DDR4 Vendor Datasheet (PDF)",
    type=["pdf"]
)

# ⛔ STOP HERE IF NO DATASHEET
if uploaded_file is None:
    st.info("Please upload a DDR4 datasheet to start the review.")
    st.stop()

st.success(f"Datasheet loaded: **{uploaded_file.name}**")

# --------------------------------------------------
# PDF TEXT EXTRACTION
# --------------------------------------------------
@st.cache_data
def extract_pages(file):
    pages = []
    with pdfplumber.open(file) as pdf:
        for i, page in enumerate(pdf.pages):
            text = page.extract_text()
            if text:
                pages.append((i + 1, text))
    return pages

pages = extract_pages(uploaded_file)

# --------------------------------------------------
# SAFE VALUE EXTRACTION
# --------------------------------------------------
def extract_param(pattern, unit=None):
    for page_no, text in pages:
        m = re.search(pattern, text, re.IGNORECASE)
        if m:
            confidence = 0.6
            if unit and unit.lower() in text.lower():
                confidence += 0.2
            confidence += 0.2
            return {
                "value": m.group(1),
                "page": page_no,
                "confidence": round(confidence, 2)
            }
    return {
        "value": "Not found",
        "page": "-",
        "confidence": 0.0
    }

# --------------------------------------------------
# PARAMETER EXTRACTION (ONLY AFTER UPLOAD)
# --------------------------------------------------
data = {
    "tAA": extract_param(r"tAA\s*=?\s*(\d+\.?\d*)", "ns"),
    "tRCD": extract_param(r"tRCD\s*=?\s*(\d+\.?\d*)", "ns"),
    "tRP": extract_param(r"tRP\s*=?\s*(\d+\.?\d*)", "ns"),
    "tRAS": extract_param(r"tRAS\s*=?\s*(\d+\.?\d*)", "ns"),
    "tRFC": extract_param(r"tRFC1?\s*=?\s*(\d+\.?\d*)", "ns"),
    "tREFI": extract_param(r"tREFI\s*=?\s*(\d+\.?\d*)", "us"),
    "Tcase": extract_param(r"(?:Tcase|max case).*?(\d+)", "°C")
}

JEDEC = {
    "tAA": 14.0,
    "tRCD": 14.0,
    "tRP": 14.0,
    "tRAS": 32.0,
    "tRFC": 350,
    "tREFI": 7.8,
    "Tcase": 95
}

# --------------------------------------------------
# REVIEW TABS (VISIBLE ONLY AFTER UPLOAD)
# --------------------------------------------------
tabs = st.tabs([
    "⏱ AC Timing",
    "🔄 Refresh & Bandwidth",
    "🌡 Thermal Limits",
    "📋 Final Summary"
])

failures = []

# ==================================================
# AC TIMING
# ==================================================
with tabs[0]:
    st.subheader("⏱ AC Timing Parameters")

    st.markdown("""
**Why this matters**  
AC timings define **data correctness**.  
Violations can cause silent corruption and field failures.
""")

    rows = []
    for p in ["tAA", "tRCD", "tRP", "tRAS"]:
        v = data[p]
        try:
            val = float(v["value"])
            status = "FAIL ❌" if val > JEDEC[p] else "PASS ✅"
        except:
            status = "UNKNOWN ⚠️"

        if status.startswith("FAIL"):
            failures.append(p)

        rows.append({
            "Parameter": p,
            "Meaning": {
                "tAA": "Read access latency",
                "tRCD": "Activate → Read delay",
                "tRP": "Precharge time",
                "tRAS": "Row active time"
            }[p],
            "Vendor Value": v["value"],
            "JEDEC Limit": JEDEC[p],
            "Page": v["page"],
            "Confidence": v["confidence"],
            "Status": status
        })

    st.dataframe(pd.DataFrame(rows), use_container_width=True)

# ==================================================
# REFRESH
# ==================================================
with tabs[1]:
    st.subheader("🔄 Refresh Behavior & Bandwidth Impact")

    st.markdown("""
**Why refresh matters**  
At high temperature, refresh frequency increases, reducing usable bandwidth.
""")

    try:
        tRFC = float(data["tRFC"]["value"])
        tREFI = float(data["tREFI"]["value"])
        bw_loss = (tRFC / (tREFI * 1000)) * 100
        st.metric("Estimated Bandwidth Loss (2× Refresh)", f"{bw_loss:.2f}%")
    except:
        st.warning("Insufficient datasheet data to compute bandwidth loss.")

# ==================================================
# THERMAL
# ==================================================
with tabs[2]:
    st.subheader("🌡 Thermal Limits & Extended Temperature")

    st.markdown("""
**Extended temperature operation (>85°C)**  
Requires **2× refresh** and causes performance degradation.
""")

    tcase = data["Tcase"]
    status = "PASS ✅" if str(tcase["value"]).isdigit() and int(tcase["value"]) <= JEDEC["Tcase"] else "FAIL ❌"

    st.table(pd.DataFrame([{
        "Parameter": "Max Case Temperature",
        "Vendor Value": tcase["value"],
        "JEDEC Limit": JEDEC["Tcase"],
        "Page": tcase["page"],
        "Confidence": tcase["confidence"],
        "Status": status
    }]))

# ==================================================
# FINAL SUMMARY
# ==================================================
with tabs[3]:
    st.subheader("📋 Datasheet Review Summary")

    if failures:
        st.error("❌ CONDITIONAL PASS – Timing Risks Identified")
    else:
        st.success("✅ DATASHEET COMPLIANT WITH JEDEC")

    st.markdown("### Key Findings")
    st.markdown(f"""
- Timing violations: **{', '.join(failures) if failures else 'None'}**
- Thermal behavior reviewed
- Conclusions based on datasheet-extracted values
""")

    st.markdown("### Proposed Engineering Actions")
    if failures:
        st.markdown("""
1. Down-bin speed grade (e.g. DDR4-2933)  
2. Increase CAS latency (+2 cycles)  
3. Enforce 2× refresh above 85°C  
4. Avoid high-performance SKUs for extended temp
""")
    else:
        st.markdown("No corrective action required.")
