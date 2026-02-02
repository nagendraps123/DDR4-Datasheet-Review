import streamlit as st

# --------------------------------------------------
# PAGE CONFIG
# --------------------------------------------------
st.set_page_config(
    page_title="JEDEC DDR4 Gatekeeper",
    layout="wide"
)

st.title("🛡️ JEDEC DDR4 Gatekeeper")
st.caption(
    "Educational + Compliance + Debug reference tool for DDR4 systems "
    "(JEDEC JESD79-4 aligned)"
)

# --------------------------------------------------
# TAB LAYOUT
# --------------------------------------------------
tabs = st.tabs([
    "1️⃣ DDR Fundamentals",
    "2️⃣ Addressing & Architecture",
    "3️⃣ Timing Parameters",
    "4️⃣ DDR4 Training",
    "5️⃣ Power Management States",
    "6️⃣ Signal Integrity",
    "7️⃣ Refresh & Retention",
    "8️⃣ Thermal & Reliability",
    "9️⃣ Failure Modes & Debug",
    "🔟 DDR3 vs DDR4 vs DDR5",
    "1️⃣1️⃣ JEDEC vs Datasheet",
    "1️⃣2️⃣ Log & Remediation"
])

# --------------------------------------------------
# TAB 1 – DDR FUNDAMENTALS
# --------------------------------------------------
with tabs[0]:
    st.header("DDR Fundamentals – How DDR4 Works")

    st.markdown("""
    **DDR (Double Data Rate)** transfers data on **both rising and falling clock edges**.
    DDR4 builds on this by increasing speed while reducing voltage and margins.
    """)

    st.subheader("Basic Command Flow")
    st.markdown("""
    ```
    PRE → ACT → READ / WRITE → PRE → REFRESH
    ```

    - **ACT** opens a row
    - **READ/WRITE** accesses columns
    - **PRE** closes the row
    - **REFRESH** preserves stored charge
    """)

    st.info(
        "Why this matters: DDR4 timing parameters only make sense "
        "when the command sequence is clearly understood."
    )

# --------------------------------------------------
# TAB 2 – ADDRESSING & ARCHITECTURE
# --------------------------------------------------
with tabs[1]:
    st.header("Addressing & Architecture")

    st.markdown("""
    DDR4 introduces **Bank Groups**, which directly impact performance and timing penalties.
    """)

    st.table([
        {"Item": "Bank Groups", "DDR4 Value": 4, "Why it matters": "Enables parallelism"},
        {"Item": "Banks per Group", "DDR4 Value": 4, "Why it matters": "Scheduling efficiency"},
        {"Item": "Row Addressing", "DDR4 Value": "15–16 bits", "Why it matters": "Density scaling"},
        {"Item": "Column Addressing", "DDR4 Value": "10 bits", "Why it matters": "Burst access"},
    ])

    st.info(
        "Why this matters: Poor bank-group awareness in controllers causes "
        "hidden latency penalties (tCCD_L)."
    )

# --------------------------------------------------
# TAB 3 – TIMING PARAMETERS
# --------------------------------------------------
with tabs[2]:
    st.header("Timing Parameters – Categorized View")

    st.markdown("""
    DDR4 timings are best understood by **function**, not memorization.
    """)

    st.table([
        {"Category": "Access", "Examples": "tAA, tRCD, tRP", "Purpose": "Read latency"},
        {"Category": "Activation", "Examples": "tRAS, tRC", "Purpose": "Row lifecycle"},
        {"Category": "Power Integrity", "Examples": "tRRD, tFAW", "Purpose": "IR drop control"},
        {"Category": "Bus Turnaround", "Examples": "tWTR, tRTW", "Purpose": "DQ contention"},
        {"Category": "Refresh", "Examples": "tRFC, tREFI", "Purpose": "Data retention"},
    ])

    st.info(
        "Why this matters: Violating one timing often impacts others. "
        "Categorization exposes systemic risk."
    )

# --------------------------------------------------
# TAB 4 – DDR4 TRAINING
# --------------------------------------------------
with tabs[3]:
    st.header("DDR4 Training – Mandatory Calibration")

    st.markdown("""
    DDR4 **cannot operate reliably without training** due to tight margins.
    """)

    st.table([
        {"Training Stage": "Write Leveling", "Purpose": "Align CK to DQS", "Failure Symptom": "No boot"},
        {"Training Stage": "Read DQS Gate", "Purpose": "Capture window", "Failure Symptom": "Random reads"},
        {"Training Stage": "VrefDQ Training", "Purpose": "Voltage centering", "Failure Symptom": "Pattern fails"},
    ])

    st.info(
        "Why this matters: Many DDR4 field failures pass JEDEC timing "
        "but fail due to marginal training."
    )

# --------------------------------------------------
# TAB 5 – POWER MANAGEMENT
# --------------------------------------------------
with tabs[4]:
    st.header("Power Management States")

    st.table([
        {"State": "Active", "Description": "Normal operation", "Exit Latency": "None"},
        {"State": "Power-Down", "Description": "Clock gated", "Exit Latency": "Short"},
        {"State": "Self-Refresh", "Description": "DRAM controls refresh", "Exit Latency": "Long"},
    ])

    st.info(
        "Why this matters: Aggressive power saving can introduce "
        "latency spikes and refresh side effects."
    )

# --------------------------------------------------
# TAB 6 – SIGNAL INTEGRITY
# --------------------------------------------------
with tabs[5]:
    st.header("Signal Integrity – Beyond Eye Diagrams")

    st.table([
        {"Issue": "Jitter", "Effect": "Horizontal eye closure"},
        {"Issue": "Noise", "Effect": "Vertical eye closure"},
        {"Issue": "Skew", "Effect": "Eye shift"},
        {"Issue": "Vref error", "Effect": "Asymmetric margin"},
    ])

    st.markdown("""
    **Conceptual Eye Representation**
    ```
    Good:      ()
    Marginal:  )(
    Closed:    ||
    ```
    """)

    st.info(
        "Why this matters: DDR4 may pass training even when margins are dangerously low."
    )

# --------------------------------------------------
# TAB 7 – REFRESH & RETENTION
# --------------------------------------------------
with tabs[6]:
    st.header("Refresh & Retention")

    st.markdown("""
    Refresh behavior changes with **density and temperature**.
    """)

    st.table([
        {"Condition": "≤ 85°C", "tREFI": "7.8 µs", "Impact": "Normal"},
        {"Condition": "> 85°C", "tREFI": "3.9 µs", "Impact": "Bandwidth loss"},
    ])

    st.markdown("""
    **Refresh Overhead Formula**
    ```
    Overhead (%) =
    (tRFC × refreshes per second) × 100
    ```
    """)

    st.info(
        "Why this matters: At high temperature, refresh can consume "
        "8–10% of memory bandwidth."
    )

# --------------------------------------------------
# TAB 8 – THERMAL & RELIABILITY
# --------------------------------------------------
with tabs[7]:
    st.header("Thermal & Reliability")

    st.table([
        {"Temperature Zone": "≤ 85°C", "Behavior": "Nominal"},
        {"Temperature Zone": "85–95°C", "Behavior": "Increased refresh"},
        {"Temperature Zone": "> 95°C", "Behavior": "Retention risk"},
    ])

    st.info(
        "Why this matters: Passing timing at room temperature does not "
        "guarantee data integrity in the field."
    )

# --------------------------------------------------
# TAB 9 – FAILURE MODES
# --------------------------------------------------
with tabs[8]:
    st.header("Failure Modes & Debug Guide")

    st.table([
        {"Symptom": "Random read errors", "Likely Cause": "Marginal Vref"},
        {"Symptom": "Fails only hot", "Likely Cause": "Refresh / leakage"},
        {"Symptom": "Cold boot failure", "Likely Cause": "Training issue"},
        {"Symptom": "Pattern failures", "Likely Cause": "Signal integrity"},
    ])

    st.info(
        "Why this matters: Mapping symptoms to root cause saves weeks of debug time."
    )

# --------------------------------------------------
# TAB 10 – DDR GENERATION COMPARISON
# --------------------------------------------------
with tabs[9]:
    st.header("DDR3 vs DDR4 vs DDR5")

    st.table([
        {"Feature": "Voltage", "DDR3": "1.5V", "DDR4": "1.2V", "DDR5": "1.1V"},
        {"Feature": "Bank Groups", "DDR3": "No", "DDR4": "Yes", "DDR5": "Enhanced"},
        {"Feature": "Training", "DDR3": "Minimal", "DDR4": "Required", "DDR5": "Mandatory"},
        {"Feature": "PMIC", "DDR3": "No", "DDR4": "No", "DDR5": "Yes"},
    ])

# --------------------------------------------------
# TAB 11 – JEDEC vs DATASHEET
# --------------------------------------------------
with tabs[10]:
    st.header("JEDEC vs Datasheet Comparison")

    st.markdown("""
    This view compares **vendor datasheet claims** against
    **JEDEC JESD79-4 requirements**.
    """)

    st.table([
        {"Parameter": "tAA", "Datasheet": "14.06 ns", "JEDEC": "≤ 13.75 ns", "Status": "FAIL"},
        {"Parameter": "tRCD", "Datasheet": "13.75 ns", "JEDEC": "≤ 13.75 ns", "Status": "PASS"},
        {"Parameter": "VDD", "Datasheet": "1.2 V", "JEDEC": "1.2V ±0.06V", "Status": "PASS"},
    ])

    st.info(
        "Why this matters: Datasheets may omit corner cases or derating conditions."
    )

# --------------------------------------------------
# TAB 12 – LOG & REMEDIATION
# --------------------------------------------------
with tabs[11]:
    st.header("Log & Remediation")

    st.error("❌ tAA violation for DDR4-3200 bin")

    st.markdown("""
    **Recommended Actions**
    - Reduce frequency to 2933 MT/s  
    - Increase CAS latency (CL)  
    - Re-evaluate training margins  
    """)

    st.success(
        "Goal: Convert failures into controlled, system-level design decisions."
    )
