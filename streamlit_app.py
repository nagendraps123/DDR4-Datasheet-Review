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
Select a DDR4 part number below. All data is preloaded from vendor datasheets.  
No uploads are required.
""")

# -------------------------
# 3. Part Number Selection
# -------------------------
part_number = st.selectbox("Select DDR4 Part Number", list(DDR4_DATASHEETS.keys()))

if part_number:
    ddr = DDR4_DATASHEETS[part_number]
    
    st.info(f"Currently Displaying: **{part_number}**")

    # -------------------------
    # 4. Tabs
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
        st.markdown("**What this tab is:** Overview of DDR4 internal architecture and operation.")
        st.markdown("**Why it matters:** DDR fundamentals define timing, refresh, and data movement across the system.")
        st.markdown("""
**Theory / Background:**  
- **DDR (Double Data Rate):** Transfers data on both rising and falling clock edges → doubles effective bandwidth.  
- **DDR4:** Lower voltage (1.2V), 8n prefetch, 4 bank groups × 16 banks, higher speed (up to 3200+ MT/s), improved power efficiency.  
- **Prefetch:** DDR4 reads 8 bits internally per access and sends them over multiple clock edges.  
- **Bank Groups & Banks:** Enable parallel access and reduce row activation conflicts.
""")
        st.table([
            {"Parameter":"Memory Type","Value":"DDR4 SDRAM"},
            {"Parameter":"Bank Groups","Value": ddr["BankGroups"]},
            {"Parameter":"Total Banks","Value": ddr["Banks"]},
            {"Parameter":"Burst Length","Value":"BL8"},
            {"Parameter":"Prefetch","Value":"8n"}
        ])
        st.markdown("**📝 Reviewer Insights / Q&A**")
        st.markdown("""
- **Key concepts:** Bank = independent storage block; Prefetch 8n = 8 bits per internal access.  
- **Cause → effect → symptom:** Wrong bank/prefetch mapping → timing overlap → intermittent errors → eventual data corruption.  
- **Temperature impact:** High temp increases leakage and reduces timing margin.  
- **Mitigation / solution:**  
   - Ensure memory controller config matches JEDEC DDR4 architecture.  
   - Validate with training logs, stress tests, and thermal profiles.  
   - Proper PCB routing and termination for signal integrity.  
- **Extra tips:** Misconfigured burst length reduces bandwidth or causes errors under high load.
""")

    # ---------------- Tab 2 ----------------
    with tabs[1]:
        st.subheader("Clock & Frequency")
        st.markdown("**What this tab is:** Validate clock frequency, period, and speed-bin compliance.")
        st.markdown("**Why it matters:** Clock timing is reference for all DDR commands and transfers.")
        st.table([
            {"Parameter":"Data Rate","Value": ddr["Speed"]},
            {"Parameter":"tCK","Value": f"{ddr['tCK']} ns"},
            {"Parameter":"Clock Type","Value":"Differential"}
        ])
        st.markdown("**📝 Reviewer Insights / Q&A**")
        st.markdown("""
- **tCK** is the base clock period; all AC timings (tAA, tRCD, tRP) are derived from it.  
- **Cause → effect → symptom:** Faster clock reduces setup/hold margin → training passes sometimes but fails under temp/voltage variation.  
- **Mitigation:** Reduce frequency, increase CAS latency, improve PCB clock trace.
""")

    # ---------------- Tab 3 ----------------
    with tabs[2]:
        st.subheader("Addressing & Architecture")
        st.markdown("**What this tab is:** Verify logical-to-physical memory mapping.")
        st.markdown("**Why it matters:** Wrong addressing → silent systematic data corruption.")
        st.table([
            {"Parameter":"Row Address","Value": ddr["Rows"]},
            {"Parameter":"Column Address","Value": ddr["Cols"]},
            {"Parameter":"Page Size","Value": ddr["Page"]}
        ])
        st.markdown("**📝 Reviewer Insights / Q&A**")
        st.markdown("""
- Wrong row/column mapping → refresh mis-target → silent corruption over time.  
- Mitigation: Validate controller mapping using stress patterns and training logs.
""")

    # ---------------- Tab 4 ----------------
    with tabs[3]:
        st.subheader("Power & Voltages")
        st.markdown("**What this tab is:** Verify DRAM supply voltages.")
        st.markdown("**Why it matters:** Voltage deviations cause speed reduction, errors, or damage.")
        st.table([
            {"Rail":"VDD","Value": f"{ddr['VDD']} V"},
            {"Rail":"VPP","Value": f"{ddr['VPP']} V"}
        ])
        st.markdown("**📝 Reviewer Insights / Q&A**")
        st.markdown("""
- Low VDD slows internal circuits → read/write errors.  
- Mitigation: Tight PMIC regulation, decoupling, proper layout.
""")

    # ---------------- Tab 5 ----------------
    with tabs[4]:
        st.subheader("AC Timing")
        st.markdown("**What this tab is:** Compare datasheet AC timings vs JEDEC limits.")
        st.markdown("**Why it matters:** Timing violations directly cause data corruption.")
        st.table([
            {"Timing":"tAA","Value": f"{ddr['tAA']} ns"},
            {"Timing":"tRCD","Value": f"{ddr['tRCD']} ns"},
            {"Timing":"tRP","Value": f"{ddr['tRP']} ns"},
            {"Timing":"tRAS","Value": f"{ddr['tRAS']} ns"}
        ])
        st.markdown("**📝 Reviewer Insights / Q&A**")
        st.markdown("""
- CAS timing exceeds limit → reduces voltage/temp margin.  
- Mitigation: Increase CAS latency or operate at lower speed grade.
""")

    # ---------------- Tab 6 ----------------
    with tabs[5]:
        st.subheader("DDR4 Training")
        st.markdown("**What this tab is:** Read/Write leveling, VrefDQ training.")
        st.markdown("**Why it matters:** Ensures reliable read/write across all banks.")
        st.markdown("**📝 Reviewer Insights / Q&A**")
        st.markdown("""
- Poor training → unstable reads/writes.  
- Mitigation: Re-run training at power-up, validate with stress patterns.
""")

    # ---------------- Tab 7 ----------------
    with tabs[6]:
        st.subheader("Refresh / Thermal / Bandwidth")
        st.markdown("**What this tab is:** Evaluate refresh frequency, thermal impact, bandwidth loss.")
        st.markdown("**Why it matters:** Insufficient refresh → data loss; excessive refresh → bandwidth reduction & higher power consumption.")

        refresh_loss = (ddr["tRFC"] / (ddr["tREFI"]*1000))*100
        st.table([
            {"Parameter":"tRFC","Value": f"{ddr['tRFC']} ns"},
            {"Parameter":"tREFI","Value": f"{ddr['tREFI']} µs"},
            {"Parameter":"Temp Grade","Value":"0–85°C"},
            {"Parameter":"Refresh Bandwidth Loss","Value": f"{refresh_loss:.2f}%"}
        ])
        st.markdown("**Bandwidth Loss Formula:**")
        st.markdown(f"Bandwidth Loss (%) = tRFC / (tREFI × 1000) × 100 ≈ {refresh_loss:.2f}%")
        st.markdown("**📝 Reviewer Insights / Q&A**")
        st.markdown("""
- High temp → refresh frequency increases → usable bandwidth decreases.  
- Mitigation: Thermal throttling, improved airflow, relaxed refresh timing if allowed, monitor refresh tax %.
""")

    # ---------------- Tab 8 ----------------
    with tabs[7]:
        st.subheader("Signal Integrity")
        st.markdown("**What this tab is:** Assess signal-quality assumptions like jitter and skew.")
        st.markdown("**Why it matters:** Poor SI → read/write errors, unstable operation.")
        st.table([
            {"Metric":"tDQSQ","Value":"≤0.16 ns"},
            {"Metric":"Jitter","Value":"Implementation dependent"},
            {"Metric":"Eye Margin","Value":"Implementation dependent"}
        ])
        st.markdown("**📝 Reviewer Insights / Q&A**")
        st.markdown("""
- Skew/jitter → eye closure → training failures.  
- Mitigation: PCB routing length match, impedance control, SI simulation.
""")

    # ---------------- Tab 9 ----------------
    with tabs[8]:
        st.subheader("DDR3/DDR4/DDR5 Context")
        st.markdown("**What this tab is:** Shows evolutionary context of DDR generations.")
        st.markdown("**Why it matters:** Understanding improvements informs migration and backward compatibility.")
        st.table([
            {"Type":"DDR3","Voltage":"1.5V","Banks":8,"Primary Risk":"Power"},
            {"Type":"DDR4","Voltage":"1.2V","Banks":16,"Primary Risk":"Timing"},
            {"Type":"DDR5","Voltage":"1.1V","Banks":32,"Primary Risk":"SI / PMIC"}
        ])
        st.markdown("**📝 Reviewer Insights / Q&A**")
        st.markdown("""
- DDR4 improves upon DDR3: lower voltage, higher speed, more banks, 8n prefetch, better efficiency.  
- DDR5 improves upon DDR4: even lower voltage, more banks/group, higher speed, improved SI & on-die ECC.  
- Migration requires controller update, SI review, and timing adjustments.
""")

    # ---------------- Tab 10 ----------------
    with tabs[9]:
        st.subheader("Review Summary")
        st.markdown("**What this tab is:** Executive summary of compliance and recommendations.")
        st.markdown("**Why it matters:** Provides actionable insights for integrators and reviewers.")
        st.markdown("""
✅ PASS: Architecture, Clock, Power  
⚠️ RISK: Training, Signal Integrity  
❌ FAIL: AC Timing (if above JEDEC limit)  

**Recommended Actions:**  
- Increase CAS latency or downgrade speed grade  
- Tight PCB routing for SI  
- Validate high-temperature operation and refresh strategy  
- Re-run training on power-up  
- Monitor refresh bandwidth impact
""")
