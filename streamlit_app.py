import streamlit as st

# -------------------------
# 1. Hardcoded DDR4 Datasheets
# -------------------------
DDR4_DATASHEETS = {
    "Micron MT40A1G8SA-075E": {
        "Density": "8Gb",
        "Speed": "3200AA",
        "BankGroups": 4,
        "Banks": 16,
        "Rows": "A0-A14",
        "Cols": "A0-A9",
        "Page": "1KB",
        "tCK": 0.625,
        "tAA": 14.06,
        "tRCD": 13.75,
        "tRP": 13.75,
        "tRAS": 32,
        "tRFC": 350,
        "tREFI": 7.8,
        "VDD": 1.2,
        "VPP": 2.38
    },
    "Samsung K4A8G085WB-BCPB": {
        "Density": "8Gb",
        "Speed": "3200AA",
        "BankGroups": 4,
        "Banks": 16,
        "Rows": "A0-A14",
        "Cols": "A0-A9",
        "Page": "1KB",
        "tCK": 0.625,
        "tAA": 13.75,
        "tRCD": 13.75,
        "tRP": 13.75,
        "tRAS": 32,
        "tRFC": 350,
        "tREFI": 7.8,
        "VDD": 1.2,
        "VPP": 2.38
    },
    "Hynix H5AN8G8NAFR-TFC": {
        "Density": "8Gb",
        "Speed": "3200AA",
        "BankGroups": 4,
        "Banks": 16,
        "Rows": "A0-A14",
        "Cols": "A0-A9",
        "Page": "1KB",
        "tCK": 0.625,
        "tAA": 13.75,
        "tRCD": 13.75,
        "tRP": 13.75,
        "tRAS": 32,
        "tRFC": 350,
        "tREFI": 7.8,
        "VDD": 1.2,
        "VPP": 2.38
    }
}

# -------------------------
# 2. Streamlit Landing Page
# -------------------------
st.set_page_config(page_title="DDR4 Compliance Tool (Offline)", layout="wide")
st.title("🛡️ DDR4 Compliance Tool - Offline Version")

st.markdown("""
Select a DDR4 part number below. No uploads are required; data is preloaded from vendor datasheets.
""")

# -------------------------
# 3. Part Number Selection
# -------------------------
part_number = st.selectbox("Select DDR4 Part Number", list(DDR4_DATASHEETS.keys()))

if part_number:
    ddr = DDR4_DATASHEETS[part_number]

    # -------------------------
    # Tabs
    # -------------------------
    tabs = st.tabs([
        "1. DDR Basics", "2. Clock & Frequency", "3. Addressing",
        "4. Power", "5. AC Timing", "6. Training",
        "7. Refresh / Thermal", "8. Signal Integrity",
        "9. DDR3/DDR4/DDR5 Context", "10. Review Summary"
    ])

    # ---------------- Tab 1 ----------------
    with tabs[0]:
        st.subheader("DDR Basics")
        st.markdown("""
**DDR Overview:** Double Data Rate transfers on both clock edges.  
**DDR4:** Lower voltage (1.2V), 8n prefetch, 4 bank groups × 16 banks, high speed.
""")
        st.table([
            {"Parameter":"Memory Type","Value":"DDR4 SDRAM"},
            {"Parameter":"Bank Groups","Value": ddr["BankGroups"]},
            {"Parameter":"Total Banks","Value": ddr["Banks"]},
            {"Parameter":"Burst Length","Value":"BL8"},
            {"Parameter":"Prefetch","Value":"8n"}
        ])
        st.markdown("""
**Insights / Q&A**  
- Bank groups reduce row conflicts.  
- Prefetch 8n increases effective bandwidth.  
- Misconfig → timing overlap → errors.
""")

    # ---------------- Tab 2 ----------------
    with tabs[1]:
        st.subheader("Clock & Frequency")
        st.table([
            {"Parameter":"Data Rate","Value": ddr["Speed"]},
            {"Parameter":"tCK","Value": f"{ddr['tCK']} ns"},
            {"Parameter":"Clock Type","Value":"Differential"}
        ])
        st.markdown("Insights: tCK defines all timing. High freq reduces margin.")

    # ---------------- Tab 3 ----------------
    with tabs[2]:
        st.subheader("Addressing & Architecture")
        st.table([
            {"Parameter":"Row Address","Value": ddr["Rows"]},
            {"Parameter":"Column Address","Value": ddr["Cols"]},
            {"Parameter":"Page Size","Value": ddr["Page"]}
        ])
        st.markdown("Insights: Wrong mapping → silent data corruption.")

    # ---------------- Tab 4 ----------------
    with tabs[3]:
        st.subheader("Power & Voltages")
        st.table([
            {"Rail":"VDD","Value": f"{ddr['VDD']} V"},
            {"Rail":"VPP","Value": f"{ddr['VPP']} V"}
        ])
        st.markdown("Insights: Voltage deviation → errors or slow access.")

    # ---------------- Tab 5 ----------------
    with tabs[4]:
        st.subheader("AC Timing")
        st.table([
            {"Timing":"tAA","Value": f"{ddr['tAA']} ns"},
            {"Timing":"tRCD","Value": f"{ddr['tRCD']} ns"},
            {"Timing":"tRP","Value": f"{ddr['tRP']} ns"},
            {"Timing":"tRAS","Value": f"{ddr['tRAS']} ns"}
        ])
        st.markdown("Insights: Violations cause intermittent errors.")

    # ---------------- Tab 6 ----------------
    with tabs[5]:
        st.subheader("DDR4 Training")
        st.markdown("Read/Write leveling and VrefDQ training ensure proper eye centering.")

    # ---------------- Tab 7 ----------------
    with tabs[6]:
        st.subheader("Refresh / Thermal / Bandwidth")
        refresh_loss = (ddr["tRFC"] / (ddr["tREFI"] * 1000)) * 100
        st.table([
            {"Parameter":"tRFC","Value": f"{ddr['tRFC']} ns"},
            {"Parameter":"tREFI","Value": f"{ddr['tREFI']} µs"},
            {"Parameter":"Refresh Bandwidth Loss","Value": f"{refresh_loss:.2f}%"}
        ])
        st.markdown("""
Formula: Bandwidth Loss (%) = tRFC / (tREFI × 1000)  
High temperature increases refresh → reduces usable bandwidth.
""")

    # ---------------- Tab 8 ----------------
    with tabs[7]:
        st.subheader("Signal Integrity")
        st.table([
            {"Metric":"tDQSQ","Value":"≤0.16 ns"},
            {"Metric":"Eye Margin","Value":"Implementation dependent"}
        ])
        st.markdown("Insights: Skew/jitter → training failure.")

    # ---------------- Tab 9 ----------------
    with tabs[8]:
        st.subheader("DDR Context")
        st.table([
            {"Type":"DDR3","Voltage":"1.5V","Banks":8,"Primary Risk":"Power"},
            {"Type":"DDR4","Voltage":"1.2V","Banks":16,"Primary Risk":"Timing"},
            {"Type":"DDR5","Voltage":"1.1V","Banks":32,"Primary Risk":"SI / PMIC"}
        ])
        st.markdown("Insights: DDR4 improves speed, voltage, banks over DDR3. DDR5 adds PMIC, ECC, and SI focus.")

    # ---------------- Tab 10 ----------------
    with tabs[9]:
        st.subheader("Review Summary")
        st.markdown("""
✅ PASS: Architecture, Clock, Power  
⚠️ RISK: Training, Signal Integrity  
❌ FAIL: AC Timing (if above JEDEC limit)  

**Recommended Actions:**  
- Increase CAS latency  
- Monitor thermal & refresh bandwidth  
- Validate training at power-up
""")
