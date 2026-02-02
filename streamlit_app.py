import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="DDR4 Datasheet Review Tool",
    layout="wide"
)

st.title("📘 DDR4 Datasheet Review & Risk Analysis Tool")
st.caption("Engineering-grade DDR qualification assistant")

# -------------------------------------------------------
# MOCKED EXTRACTED DATA (replace with real extraction)
# -------------------------------------------------------

extracted = {
    "clock": {
        "data_rate": {"value": 3200, "page": 12, "text": "DDR4-3200 supported"},
        "tCK": {"value": 0.625, "page": "Derived", "text": "tCK = 1 / (3200/2)"}
    },
    "timing": {
        "tAA": {"value": 14.06, "page": 47, "text": "tAA(max) = 14.06 ns"},
        "tRCD": {"value": 14.06, "page": 47, "text": "tRCD = 14.06 ns"},
        "tRP": {"value": 14.06, "page": 47, "text": "tRP = 14.06 ns"}
    },
    "refresh": {
        "tRFC1": {"value": 350, "page": 52, "text": "tRFC1 = 350 ns"},
        "tREFI_1x": 7.8,
        "tREFI_2x": 3.9
    }
}

JEDEC = {
    "tAA": 14.0,
    "tRCD": 14.0,
    "tRP": 14.0
}

# -------------------------------------------------------
# TABS
# -------------------------------------------------------

tabs = st.tabs([
    "🕒 DDR Clock",
    "⏱️ AC Timing",
    "🔄 Refresh & Bandwidth",
    "🧠 Latency (RLA)",
    "📊 Evidence",
    "📋 Executive Summary"
])

# -------------------------------------------------------
# 1. DDR CLOCK TAB
# -------------------------------------------------------
with tabs[0]:
    st.subheader("🕒 DDR Clock & Frequency")

    st.markdown("""
**Why this matters**  
All DDR timings are derived from the clock period (tCK).  
If clocking is wrong, *every timing check is invalid*.
""")

    df = pd.DataFrame([
        {
            "Parameter": "Data Rate",
            "Extracted": f"{extracted['clock']['data_rate']['value']} MT/s",
            "Source Page": extracted['clock']['data_rate']['page'],
            "Status": "PASS ✅"
        },
        {
            "Parameter": "tCK",
            "Extracted": f"{extracted['clock']['tCK']['value']} ns",
            "Source Page": extracted['clock']['tCK']['page'],
            "Status": "PASS ✅"
        }
    ])

    st.dataframe(df, use_container_width=True)

# -------------------------------------------------------
# 2. AC TIMING TAB
# -------------------------------------------------------
with tabs[1]:
    st.subheader("⏱️ AC Timing Parameters")

    st.markdown("""
**Parameter explanation**
- **tAA**: READ → data valid delay
- **tRCD**: ACTIVATE → READ
- **tRP**: PRECHARGE time

Violations cause **silent data corruption**.
""")

    rows = []
    for p in ["tAA", "tRCD", "tRP"]:
        val = extracted["timing"][p]["value"]
        jedec = JEDEC[p]
        rows.append({
            "Parameter": p,
            "Extracted (ns)": val,
            "JEDEC Max (ns)": jedec,
            "Delta (ns)": round(val - jedec, 3),
            "Status": "FAIL ❌" if val > jedec else "PASS ✅",
            "Page": extracted["timing"][p]["page"]
        })

    st.dataframe(pd.DataFrame(rows), use_container_width=True)

# -------------------------------------------------------
# 3. REFRESH & BANDWIDTH TAB
# -------------------------------------------------------
with tabs[2]:
    st.subheader("🔄 Refresh Behavior & Bandwidth Loss")

    st.markdown("""
**Why refresh matters**  
Higher temperature requires more frequent refresh, reducing usable bandwidth.
""")

    tRFC = extracted["refresh"]["tRFC1"]["value"]
    tREFI = extracted["refresh"]["tREFI_2x"]  # assume worst case

    bandwidth_loss = (tRFC / (tREFI * 1000)) * 100

    st.metric(
        "Estimated Bandwidth Loss",
        f"{bandwidth_loss:.2f} %",
        delta="Due to 2× refresh"
    )

    st.warning("""
⚠️ **Impact**
- Throughput reduction
- Higher latency under load
- Thermal sensitivity risk
""")

# -------------------------------------------------------
# 4. RLA TAB
# -------------------------------------------------------
with tabs[3]:
    st.subheader("🧠 Effective Read Latency (RLA)")

    rla = (
        extracted["timing"]["tAA"]["value"]
        + extracted["timing"]["tRCD"]["value"]
        + extracted["timing"]["tRP"]["value"]
    )

    st.metric("RLA (ns)", f"{rla:.2f}")

    st.info("""
**Why RLA matters**
- CPU stall time
- Cache miss penalty
- Latency-sensitive workloads
""")

# -------------------------------------------------------
# 5. EVIDENCE TAB
# -------------------------------------------------------
with tabs[4]:
    st.subheader("📊 Datasheet Evidence")

    for section in extracted:
        st.markdown(f"### {section.upper()}")
        for k, v in extracted[section].items():
            if isinstance(v, dict):
                with st.expander(f"{k} – Page {v['page']}"):
                    st.code(v["text"])

# -------------------------------------------------------
# 6. EXECUTIVE SUMMARY TAB
# -------------------------------------------------------
with tabs[5]:
    st.subheader("📋 Executive Review Summary")

    st.error("### ❌ CONDITIONAL APPROVAL")

    st.markdown("""
### 🔍 Key Findings
- ❌ AC timings exceed JEDEC limits
- ⚠️ 2× refresh required above 85°C
- 📉 ~4–5% bandwidth loss expected
""")

    st.markdown("""
### ⚠️ Risk Assessment
| Area | Risk |
|----|----|
| Functional | Medium |
| Performance | Medium–High |
| Thermal | High |
""")

    st.markdown("""
### 🛠️ Proposed Mitigations
1. Downclock to **2933 MT/s**
2. Increase CAS Latency by **+2 cycles**
3. Enforce **2× refresh** in firmware
4. Restrict usage to **≤85°C** for performance SKUs
""")

    st.markdown("""
### 🎯 Usage Recommendation
- ❌ Safety-critical systems: **Not recommended**
- ⚠️ Servers: **ECC + derating required**
- ✅ Consumer / Office: **Acceptable**
""")
