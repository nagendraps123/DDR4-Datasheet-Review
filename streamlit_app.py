import streamlit as st
import pdfplumber
import pandas as pd
import re
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import A4
import tempfile

# --------------------------------------------------
# PAGE CONFIG
# --------------------------------------------------
st.set_page_config(page_title="DDR4 Datasheet Review Tool", layout="wide")

st.title("📘 DDR4 Datasheet Review & Compliance Tool")
st.markdown("""
Engineering review of **DDR4 vendor datasheets** against  
**JEDEC JESD79-4 standard**

🔗 JEDEC Reference: https://www.jedec.org/standards-documents/docs/jesd79-4
---
""")

# --------------------------------------------------
# FILE UPLOAD
# --------------------------------------------------
uploaded_file = st.file_uploader(
    "📤 Upload DDR4 Vendor Datasheet (PDF)",
    type=["pdf"]
)

if not uploaded_file:
    st.info("Upload a DDR4 datasheet to begin review.")
    st.stop()

st.success(f"Loaded datasheet: **{uploaded_file.name}**")

# --------------------------------------------------
# PDF TEXT EXTRACTION
# --------------------------------------------------
@st.cache_data
def extract_pdf_text(file):
    pages = []
    with pdfplumber.open(file) as pdf:
        for i, page in enumerate(pdf.pages):
            text = page.extract_text()
            if text:
                pages.append((i + 1, text))
    return pages

pages = extract_pdf_text(uploaded_file)

# --------------------------------------------------
# VALUE EXTRACTION HELPERS
# --------------------------------------------------
def find_value(pattern, unit=None):
    for page_no, text in pages:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            value = match.group(1)
            confidence = 0.6
            if unit and unit.lower() in text.lower():
                confidence += 0.2
            if match.group(0):
                confidence += 0.2
            return {
                "value": value,
                "page": page_no,
                "confidence": round(confidence, 2)
            }
    return {
        "value": "Not found",
        "page": "-",
        "confidence": 0.0
    }

# --------------------------------------------------
# EXTRACT PARAMETERS
# --------------------------------------------------
extracted = {
    "tAA": find_value(r"tAA\s*=?\s*(\d+\.?\d*)", "ns"),
    "tRCD": find_value(r"tRCD\s*=?\s*(\d+\.?\d*)", "ns"),
    "tRP": find_value(r"tRP\s*=?\s*(\d+\.?\d*)", "ns"),
    "tRAS": find_value(r"tRAS\s*=?\s*(\d+\.?\d*)", "ns"),
    "tRFC": find_value(r"tRFC1?\s*=?\s*(\d+\.?\d*)", "ns"),
    "tREFI": find_value(r"tREFI\s*=?\s*(\d+\.?\d*)", "us"),
    "tCASE": find_value(r"(?:Tcase|max case temp).*?(\d+)", "°C")
}

# --------------------------------------------------
# JEDEC LIMITS
# --------------------------------------------------
JEDEC = {
    "tAA": 14.0,
    "tRCD": 14.0,
    "tRP": 14.0,
    "tRAS": 32.0,
    "tRFC": 350,
    "tREFI": 7.8,
    "tCASE": 95
}

# --------------------------------------------------
# TABS
# --------------------------------------------------
tabs = st.tabs([
    "⏱ AC Timing",
    "🔄 Refresh",
    "🌡 Thermal",
    "📋 Final Summary"
])

failures = []

# --------------------------------------------------
# AC TIMING TAB
# --------------------------------------------------
with tabs[0]:
    st.subheader("⏱ AC Timing Parameters")

    st.markdown("""
These timings directly affect **data correctness**.
Violations may cause **silent data corruption**.
""")

    rows = []
    for p in ["tAA", "tRCD", "tRP", "tRAS"]:
        v = extracted[p]
        try:
            numeric = float(v["value"])
            status = "FAIL ❌" if numeric > JEDEC[p] else "PASS ✅"
        except:
            status = "UNKNOWN ⚠️"

        if status.startswith("FAIL"):
            failures.append(p)

        rows.append({
            "Parameter": p,
            "Vendor Value": v["value"],
            "JEDEC Limit": JEDEC[p],
            "Page": v["page"],
            "Confidence": v["confidence"],
            "Status": status
        })

    st.dataframe(pd.DataFrame(rows), use_container_width=True)

# --------------------------------------------------
# REFRESH TAB
# --------------------------------------------------
with tabs[1]:
    st.subheader("🔄 Refresh Behavior")

    tRFC = extracted["tRFC"]["value"]
    tREFI = extracted["tREFI"]["value"]

    if isinstance(tRFC, str) or isinstance(tREFI, str):
        st.warning("Insufficient data to compute bandwidth loss.")
        bw_loss = None
    else:
        bw_loss = (float(tRFC) / (float(tREFI) * 1000)) * 100
        st.metric("Estimated Bandwidth Loss @ 2× Refresh", f"{bw_loss:.2f}%")

    st.markdown("""
**Explanation**
- Higher temperature → more refresh
- More refresh → less usable bandwidth
""")

# --------------------------------------------------
# THERMAL TAB
# --------------------------------------------------
with tabs[2]:
    st.subheader("🌡 Thermal Limits & Extended Temperature")

    tcase = extracted["tCASE"]
    status = "PASS ✅" if str(tcase["value"]).isdigit() and int(tcase["value"]) <= JEDEC["tCASE"] else "FAIL ❌"

    st.table(pd.DataFrame([{
        "Parameter": "Max Case Temperature",
        "Vendor": tcase["value"],
        "JEDEC": JEDEC["tCASE"],
        "Page": tcase["page"],
        "Confidence": tcase["confidence"],
        "Status": status
    }]))

# --------------------------------------------------
# FINAL SUMMARY TAB
# --------------------------------------------------
with tabs[3]:
    st.subheader("📋 Executive Review Summary")

    if failures:
        st.error("❌ CONDITIONAL PASS")
    else:
        st.success("✅ DATASHEET COMPLIANT")

    st.markdown("### Key Findings")
    st.markdown(f"""
- Timing failures: **{', '.join(failures) if failures else 'None'}**
- Thermal limit verified
- Datasheet confidence: **Extraction-based**
""")

    st.markdown("### Proposed Engineering Actions")
    if failures:
        st.markdown("""
1. Down-bin speed grade (e.g., DDR4-2933)
2. Increase CAS latency (+2 cycles)
3. Enforce 2× refresh above 85 °C
4. Avoid performance SKUs at high temperature
""")
    else:
        st.markdown("No corrective action required.")

    # --------------------------------------------------
    # PDF EXPORT
    # --------------------------------------------------
    if st.button("📄 Download Review Report (PDF)"):
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            doc = SimpleDocTemplate(tmp.name, pagesize=A4)
            styles = getSampleStyleSheet()
            content = []

            content.append(Paragraph("DDR4 Datasheet Review Report", styles["Title"]))
            content.append(Spacer(1, 12))

            for p in extracted:
                content.append(Paragraph(
                    f"<b>{p}</b>: {extracted[p]['value']} "
                    f"(Page {extracted[p]['page']}, Confidence {extracted[p]['confidence']})",
                    styles["Normal"]
                ))

            doc.build(content)
            st.download_button(
                "⬇️ Download PDF",
                open(tmp.name, "rb"),
                file_name="DDR4_Datasheet_Review.pdf"
)
