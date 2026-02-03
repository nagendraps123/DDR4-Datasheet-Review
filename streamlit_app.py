import streamlit as st

# -------------------------------
# Page Config
# -------------------------------
st.set_page_config(
    page_title="DDR Datasheet Review Tool",
    layout="wide"
)

# -------------------------------
# Hard-coded DDR4 Datasheet Models
# -------------------------------
DDR_DATABASE = {
    "Micron MT40A1G8SA-075E (Golden Sample)": {
        "vendor": "Micron",
        "density": "8Gb",
        "speed_bin": "DDR4-3200AA",
        "jedec": "JESD79-4C",
        "tAA": 13.75,
        "tRCD": 13.75,
        "tRP": 13.75,
        "tRAS": 32,
        "tRFC": 350,
        "temp_grade": "0–85°C",
        "dqsq": 0.15
    },
    "Samsung K4A8G085WB (Clock Marginal)": {
        "vendor": "Samsung",
        "density": "8Gb",
        "speed_bin": "DDR4-3200",
        "jedec": "JESD79-4C",
        "tAA": 14.2,
        "tRCD": 14.0,
        "tRP": 14.0,
        "tRAS": 33,
        "tRFC": 360,
        "temp_grade": "0–85°C",
        "dqsq": 0.17
    },
    "SK Hynix H5AN8G6NC (Thermal / Refresh Risk)": {
        "vendor": "SK Hynix",
        "density": "8Gb",
        "speed_bin": "DDR4-3200",
        "jedec": "JESD79-4C",
        "tAA": 13.9,
        "tRCD": 13.9,
        "tRP": 13.9,
        "tRAS": 32,
        "tRFC": 420,
        "temp_grade": "0–95°C",
        "dqsq": 0.16
    },
    "Generic DDR4-3200 (Multiple Failures)": {
        "vendor": "Generic",
        "density": "8Gb",
        "speed_bin": "DDR4-3200",
        "jedec": "JESD79-4C",
        "tAA": 15.0,
        "tRCD": 15.0,
        "tRP": 15.0,
        "tRAS": 34,
        "tRFC": 450,
        "temp_grade": "0–85°C",
        "dqsq": 0.21
    }
}

JEDEC_LIMITS = {
    "tAA": 13.75,
    "tRCD": 13.75,
    "tRP": 13.75,
    "tRFC": 350,
    "tREFI": 7.8,
    "dqsq": 0.16
}

# -------------------------------
# Landing Page
# -------------------------------
st.title("📊 DDR Datasheet Review & JEDEC Audit Tool")

st.info(
    """
    **Offline / Local Usage Notice**  
    This tool is designed to run completely **offline**.  
    If you like the results generated here, you can download the full code package
    and run it locally on your PC to review **private datasheets** without uploading
    them to any public server.
    """
)

st.markdown(
    """
    ### What this tool does
    - Performs a **structured technical review** of DDR SDRAM datasheets  
    - Maps parameters against **JEDEC standards**
    - Explains **cause → effect → system-level symptoms**
    - Demonstrates **PASS / MARGINAL / FAIL** scenarios
    - Suggests **engineering mitigations**
    """
)

# -------------------------------
# Part Selection
# -------------------------------
st.sidebar.header("📂 Select DDR Part")
selected_part = st.sidebar.radio(
    "Available DDR4 Datasheets",
    list(DDR_DATABASE.keys())
)

data = DDR_DATABASE[selected_part]

st.success(f"🔍 Currently Reviewing: **{selected_part} ({data['vendor']})**")

# -------------------------------
# Tabs
# -------------------------------
tabs = st.tabs([
    "DDR Basics",
    "Clock & Frequency",
    "Addressing & Architecture",
    "Power & Voltages",
    "AC Timing",
    "Signal Integrity",
    "Refresh, Thermal & Bandwidth",
    "Failure Modes & Propagation",
    "DDR3 vs DDR4 vs DDR5",
    "Review Summary"
])

# -------------------------------
# TAB 1 – DDR BASICS
# -------------------------------
with tabs[0]:
    st.subheader("What this tab is")
    st.write("A foundational explanation of DDR memory operation and DDR4 architecture.")

    st.subheader("Why it matters")
    st.write(
        "Most DDR failures originate from incorrect architectural assumptions rather than silicon defects."
    )

    st.subheader("DDR Theory")
    st.write(
        """
        DDR transfers data on both clock edges.
        DDR4 introduces bank groups, tighter timing margins, and lower voltage,
        making system-level design critical.
        """
    )

    st.subheader("Reviewer Q&A – Insights")
    st.markdown(
        """
        **Q: Why do DDR4 failures appear random?**  
        Because margin violations depend on temperature, voltage, and noise.

        **Cause → Effect → Symptom**  
        Wrong assumptions → margin erosion → intermittent field failures.

        **Mitigation**  
        Always validate controller configuration against JEDEC architecture.
        """
    )

# -------------------------------
# TAB 2 – CLOCK & FREQUENCY
# -------------------------------
with tabs[1]:
    st.subheader("What this tab is")
    st.write("Validation of operating frequency and clock-derived timings.")

    st.subheader("Why it matters")
    st.write("Clock errors scale into every AC timing parameter.")

    st.markdown(f"- CAS Access Time (tAA): {data['tAA']} ns")

    if data["tAA"] > JEDEC_LIMITS["tAA"]:
        st.error("❌ Clock timing violation → reduced setup/hold margin.")
        st.markdown("**Mitigation:** Reduce speed grade or increase CAS latency.")

# -------------------------------
# TAB 3 – ADDRESSING
# -------------------------------
with tabs[2]:
    st.subheader("What this tab is")
    st.write("Verification of addressing and memory organization.")

    st.subheader("Why it matters")
    st.write("Addressing errors cause silent corruption.")

# -------------------------------
# TAB 4 – POWER
# -------------------------------
with tabs[3]:
    st.subheader("What this tab is")
    st.write("Validation of DRAM supply assumptions.")

    st.subheader("Why it matters")
    st.write("Voltage noise directly affects eye margin.")

# -------------------------------
# TAB 5 – AC TIMING
# -------------------------------
with tabs[4]:
    st.subheader("What this tab is")
    st.write("AC timing vs JEDEC limits.")

    st.markdown(
        f"""
        - tAA: {data['tAA']} ns  
        - tRCD: {data['tRCD']} ns  
        - tRP: {data['tRP']} ns  
        """
    )

    if data["tAA"] > JEDEC_LIMITS["tAA"]:
        st.error("❌ AC timing FAIL detected.")

# -------------------------------
# TAB 6 – SIGNAL INTEGRITY
# -------------------------------
with tabs[5]:
    st.subheader("What this tab is")
    st.write("High-speed signal integrity assumptions.")

    st.subheader("Why it matters")
    st.write("Eye closure is the #1 root cause of DDR field failures.")

    if data["dqsq"] > JEDEC_LIMITS["dqsq"]:
        st.error("❌ Eye margin violation (DQSQ).")
        st.markdown("**Mitigation:** Improve routing, termination, reduce speed.")

# -------------------------------
# TAB 7 – REFRESH, THERMAL & BANDWIDTH
# -------------------------------
with tabs[6]:
    st.subheader("What this tab is")
    st.write("Refresh overhead and thermal behavior.")

    refresh_loss = (data["tRFC"] / (JEDEC_LIMITS["tREFI"] * 1000)) * 100

    st.markdown(f"- Refresh Bandwidth Loss: **{refresh_loss:.2f}%**")

    if data["tRFC"] > JEDEC_LIMITS["tRFC"]:
        st.error("❌ Excessive refresh → bandwidth & power risk.")

    if "95" in data["temp_grade"]:
        st.warning("⚠️ Extended temperature → doubled refresh risk.")

# -------------------------------
# TAB 8 – FAILURE MODES
# -------------------------------
with tabs[7]:
    st.subheader("What this tab is")
    st.write("Mapping violations to real-world failures.")

    st.markdown(
        """
        - Clock margin loss → CRC / boot failures  
        - Eye closure → random bit errors  
        - Thermal refresh → throughput collapse  
        """
    )

# -------------------------------
# TAB 9 – DDR CONTEXT
# -------------------------------
with tabs[8]:
    st.subheader("DDR Evolution Context")

    st.markdown(
        """
        **DDR3:** Voltage-limited  
        **DDR4:** Timing-limited  
        **DDR5:** Power & SI-limited
        """
    )

# -------------------------------
# TAB 10 – SUMMARY
# -------------------------------
with tabs[9]:
    st.subheader("Final Review Summary")

    st.markdown(
        """
        **Key Risks Identified**
        - Clock margin
        - Refresh overhead
        - Eye integrity

        **Recommended Actions**
        - Speed derating
        - SI simulation
        - Thermal validation
        """
    )
