import streamlit as st
import pandas as pd

# -------------------------------
# Page Config
# -------------------------------
st.set_page_config(page_title="DDR4 Datasheet Review Tool", layout="wide")

# -------------------------------
# Hardcoded DDR4 Parts Database
# -------------------------------
DDR_DATABASE = {
    "Micron MT40A1G8SA-075E (Golden)": {
        "vendor": "Micron",
        "density": "8Gb",
        "speed_bin": "DDR4-3200AA",
        "jedec": "JESD79-4C",
        "tCK": 0.625,
        "tAA": 13.75,
        "tRCD": 13.75,
        "tRP": 13.75,
        "tRAS": 32,
        "tRFC": 350,
        "VDD": 1.2,
        "VPP": 2.5,
        "TempGrade": "0–85°C",
        "tREFI": 7.8,
        "SignalMargin": 0.16,
        "EyeHeight": 0.25,
        "Jitter": 0.05,
        "TrainingPass": True,
        "ClockSkew": 0.05,
        "PCBLengthMismatch": 0.1
    },
    "Samsung K4A8G085WB-BCRC (Marginal)": {
        "vendor": "Samsung",
        "density": "8Gb",
        "speed_bin": "DDR4-3200",
        "jedec": "JESD79-4C",
        "tCK": 0.625,
        "tAA": 14.0,
        "tRCD": 13.9,
        "tRP": 14.1,
        "tRAS": 32,
        "tRFC": 355,
        "VDD": 1.2,
        "VPP": 2.5,
        "TempGrade": "0–85°C",
        "tREFI": 7.8,
        "SignalMargin": 0.18,
        "EyeHeight": 0.22,
        "Jitter": 0.08,
        "TrainingPass": True,
        "ClockSkew": 0.08,
        "PCBLengthMismatch": 0.15
    },
    "Hynix H5AN8G8NAFR-TF (Failure 1)": {
        "vendor": "Hynix",
        "density": "8Gb",
        "speed_bin": "DDR4-3200",
        "jedec": "JESD79-4C",
        "tCK": 0.625,
        "tAA": 15.0,
        "tRCD": 15.0,
        "tRP": 15.0,
        "tRAS": 32,
        "tRFC": 380,
        "VDD": 1.25,
        "VPP": 2.6,
        "TempGrade": "0–95°C",
        "tREFI": 7.8,
        "SignalMargin": 0.25,
        "EyeHeight": 0.15,
        "Jitter": 0.12,
        "TrainingPass": False,
        "ClockSkew": 0.12,
        "PCBLengthMismatch": 0.25
    },
    "Micron MT40A2G8SA-075E (Failure 2)": {
        "vendor": "Micron",
        "density": "16Gb",
        "speed_bin": "DDR4-3200AA",
        "jedec": "JESD79-4C",
        "tCK": 0.625,
        "tAA": 16.0,
        "tRCD": 16.0,
        "tRP": 16.0,
        "tRAS": 33,
        "tRFC": 400,
        "VDD": 1.25,
        "VPP": 2.65,
        "TempGrade": "0–95°C",
        "tREFI": 7.8,
        "SignalMargin": 0.3,
        "EyeHeight": 0.12,
        "Jitter": 0.15,
        "TrainingPass": False,
        "ClockSkew": 0.15,
        "PCBLengthMismatch": 0.3
    }
}

# -------------------------------
# Landing Page
# -------------------------------
st.title("📊 DDR4 Datasheet Review & JEDEC Audit Tool")
st.info(
    """
    **Offline Mode:**  
    This tool runs fully offline using hardcoded DDR4 datasheets.  
    You can also download this package and run it locally to review your own private datasheets.  
    No data is uploaded to any server.
    """
)
st.markdown("""
### Purpose:
- Compare DDR4 datasheet parameters with **JEDEC JESD79-4C**.
- Highlight **marginal, failure, and golden samples**.
- Provide **root cause analysis, reviewer insights, and mitigation guidance**.
- Help engineers understand **thermal, refresh, AC timing, clock, signal integrity, and power impacts**.
""")

# -------------------------------
# Part Selection
# -------------------------------
st.sidebar.header("📂 Select DDR4 Part")
selected_part = st.sidebar.radio("Available DDR4 Parts", list(DDR_DATABASE.keys()))
data = DDR_DATABASE[selected_part]
st.success(f"🔍 Currently Reviewing: **{selected_part} ({data['vendor']})**")

# -------------------------------
# Tabs
# -------------------------------
tabs = st.tabs([
    "1. DDR Basics", "2. Clock & Frequency", "3. Addressing & Architecture",
    "4. Power & Voltages", "5. AC Timing", "6. Training",
    "7. Refresh/Thermal/Bandwidth", "8. Signal Integrity", "9. DDR3/4/5 Context",
    "10. Review Summary"
])

# -------------------------------
# Helper for color-coded status
# -------------------------------
def status_color(value, jedec_limit, param_type='max'):
    if param_type=='max':
        if value <= jedec_limit:
            return "✅ PASS"
        elif value <= jedec_limit*1.05:
            return "⚠️ MARGINAL"
        else:
            return "❌ FAIL"
    elif param_type=='min':
        if value >= jedec_limit:
            return "✅ PASS"
        elif value >= jedec_limit*0.95:
            return "⚠️ MARGINAL"
        else:
            return "❌ FAIL"

# -------------------------------
# Tab 1 – DDR Basics
# -------------------------------
with tabs[0]:
    st.subheader("What this tab is")
    st.write("Overview of DDR4 internal architecture, bank groups, prefetch, burst length, and timing fundamentals.")
    st.subheader("Why it matters")
    st.write("DDR fundamentals determine timing, refresh, and data movement across the system.")
    st.subheader("Key Parameters / Root Causes")
    df_basics = pd.DataFrame([
        {"Parameter":"Memory Type","Datasheet":"DDR4 SDRAM","JEDEC":"DDR4 SDRAM","Status":"✅ PASS"},
        {"Parameter":"Bank Groups","Datasheet":4,"JEDEC":4,"Status":"✅ PASS"},
        {"Parameter":"Total Banks","Datasheet":16,"JEDEC":16,"Status":"✅ PASS"},
        {"Parameter":"Burst Length","Datasheet":"BL8","JEDEC":"BL8","Status":"✅ PASS"},
        {"Parameter":"Prefetch","Datasheet":"8n","JEDEC":"8n","Status":"✅ PASS"},
    ])
    st.table(df_basics)
    st.subheader("Reviewer Insights / Notes (Q&A)")
    st.markdown("""
**Q: Why bank groups?**  
Enable parallel access and reduce row conflicts, increasing throughput.  

**Q: What is prefetch (8n)?**  
8 bits are fetched internally per access, serialized externally for high bandwidth.  

**Mitigation:**  
Ensure memory controller configuration matches DDR4 JEDEC spec.
""")

# -------------------------------
# Tab 2 – Clock & Frequency
# -------------------------------
with tabs[1]:
    st.subheader("What this tab is")
    st.write("Check DDR4 clock period, frequency, and jitter.")
    st.subheader("Why it matters")
    st.write("All AC timings derive from tCK; skew/jitter reduce timing margin.")
    df_clock = pd.DataFrame([
        {"Parameter":"tCK (ns)","Datasheet":data["tCK"],"JEDEC":0.625,"Status":status_color(data["tCK"],0.625,'max')},
        {"Parameter":"Jitter (ns)","Datasheet":data["Jitter"],"JEDEC":0.16,"Status":status_color(data["Jitter"],0.16,'max')},
        {"Parameter":"Clock Skew (ns)","Datasheet":data["ClockSkew"],"JEDEC":0.1,"Status":status_color(data["ClockSkew"],0.1,'max')},
        {"Parameter":"PCB Trace Length Mismatch (mm)","Datasheet":data["PCBLengthMismatch"],"JEDEC":0.2,"Status":status_color(data["PCBLengthMismatch"],0.2,'max')}
    ])
    st.table(df_clock)
    st.subheader("Reviewer Insights / Notes (Q&A)")
    st.markdown("""
**Cause → Effect → Symptom:** Clock skew/jitter → setup/hold violations → training errors.  

**Mitigation:** Tight PCB routing, matched trace lengths, proper termination.
""")

# -------------------------------
# Tab 3 – Addressing & Architecture
# -------------------------------
with tabs[2]:
    st.subheader("What this tab is")
    st.write("Logical-to-physical mapping of banks, rows, columns, and pages.")
    st.subheader("Why it matters")
    st.write("Incorrect addressing leads to silent corruption.")
    df_addr = pd.DataFrame([
        {"Parameter":"Bank Groups","Datasheet":4,"JEDEC":4,"Status":"✅ PASS"},
        {"Parameter":"Banks / Group","Datasheet":4,"JEDEC":4,"Status":"✅ PASS"},
        {"Parameter":"Row Address","Datasheet":"A0–A14","JEDEC":"A0–A14","Status":"✅ PASS"},
        {"Parameter":"Column Address","Datasheet":"A0–A9","JEDEC":"A0–A9","Status":"✅ PASS"},
        {"Parameter":"Page Size","Datasheet":"1KB","JEDEC":"1KB","Status":"✅ PASS"}
    ])
    st.table(df_addr)
    st.subheader("Reviewer Insights / Notes (Q&A)")
    st.markdown("Validate controller mapping using stress tests; row/col misalignment causes silent corruption.")

# -------------------------------
# Tab 4 – Power & Voltages
# -------------------------------
with tabs[3]:
    st.subheader("What this tab is")
    st.write("Supply voltages and tolerances.")
    st.subheader("Why it matters")
    st.write("Voltage deviation affects speed, retention, and noise immunity.")
    df_power = pd.DataFrame([
        {"Parameter":"VDD (V)","Datasheet":data["VDD"],"JEDEC":1.2,"Status":status_color(data["VDD"],1.2,'max')},
        {"Parameter":"VPP (V)","Datasheet":data["VPP"],"JEDEC":2.5,"Status":status_color(data["VPP"],2.5,'max')}
    ])
    st.table(df_power)
    st.subheader("Reviewer Insights / Notes (Q&A)")
    st.markdown("Low/high voltage causes errors; mitigate with tight PMIC, decoupling, and layout optimization.")

# -------------------------------
# Tab 5 – AC Timing
# -------------------------------
with tabs[4]:
    st.subheader("What this tab is")
    st.write("Read/write access timing compared to JEDEC spec.")
    st.subheader("Why it matters")
    st.write("Violating tAA/tRCD/tRP/tRAS causes errors and reduces margin.")
    df_ac = pd.DataFrame([
        {"Parameter":"tAA (ns)","Datasheet":data["tAA"],"JEDEC":13.75,"Status":status_color(data["tAA"],13.75)},
        {"Parameter":"tRCD (ns)","Datasheet":data["tRCD"],"JEDEC":13.75,"Status":status_color(data["tRCD"],13.75)},
        {"Parameter":"tRP (ns)","Datasheet":data["tRP"],"JEDEC":13.75,"Status":status_color(data["tRP"],13.75)},
        {"Parameter":"tRAS (ns)","Datasheet":data["tRAS"],"JEDEC":32,"Status":status_color(data["tRAS"],32,'min')}
    ])
    st.table(df_ac)
    st.subheader("Reviewer Insights / Notes (Q&A)")
    st.markdown("Higher-than-spec timings reduce margin; lower timings may cause unstable operation.")

# -------------------------------
# Tab 6 – Training
# -------------------------------
with tabs[5]:
    st.subheader("What this tab is")
    st.write("DDR4 read/write leveling and VrefDQ training.")
    st.subheader("Why it matters")
    st.write("Ensures all banks operate reliably.")
    df_training = pd.DataFrame([
        {"Parameter":"Training Pass","Datasheet":data["TrainingPass"],"JEDEC":"Pass","Status":"✅ PASS" if data["TrainingPass"] else "❌ FAIL"}
    ])
    st.table(df_training)
    st.subheader("Reviewer Insights / Notes (Q&A)")
    st.markdown("Training failures → unstable read/write. Mitigate with controller firmware updates and retesting.")

# -------------------------------
# Tab 7 – Refresh / Thermal / Bandwidth
# -------------------------------
with tabs[6]:
    st.subheader("What this tab is")
    st.write("Refresh cycles, tRFC, thermal impact, and bandwidth reduction.")
    st.subheader("Why it matters")
    st.write("Refresh steals bandwidth; thermal increase may double refresh frequency.")
    bandwidth_loss = (data["tRFC"] / (data["tREFI"]*1000))*100
    df_refresh = pd.DataFrame([
        {"Parameter":"tRFC (ns)","Datasheet":data["tRFC"],"JEDEC":350,"Status":status_color(data["tRFC"],350)},
        {"Parameter":"tREFI (µs)","Datasheet":data["tREFI"],"JEDEC":7.8,"Status":"✅ PASS"},
        {"Parameter":"Temperature Grade","Datasheet":data["TempGrade"],"JEDEC":"0–85°C","Status":"✅ PASS"},
        {"Parameter":"Bandwidth Loss (%)","Datasheet":f"{bandwidth_loss:.2f}","JEDEC":"≤5%","Status":"✅ PASS" if bandwidth_loss<=5 else "⚠️ MARGINAL" if bandwidth_loss<=6 else "❌ FAIL"}
    ])
    st.table(df_refresh)
    st.subheader("Reviewer Insights / Notes (Q&A)")
    st.markdown("High temp → increased refresh → reduces bandwidth. Mitigate with airflow, thermal throttling, or relax refresh timing if allowed.")

# -------------------------------
# Tab 8 – Signal Integrity
# -------------------------------
with tabs[7]:
    st.subheader("What this tab is")
    st.write("Signal quality, eye diagram, skew, and reflections.")
    st.subheader("Why it matters")
    st.write("Poor SI leads to read/write errors and training failures.")
    df_si = pd.DataFrame([
        {"Parameter":"Signal Margin (ns)","Datasheet":data["SignalMargin"],"JEDEC":0.16,"Status":status_color(data["SignalMargin"],0.16)},
        {"Parameter":"Eye Height (V)","Datasheet":data["EyeHeight"],"JEDEC":0.2,"Status":status_color(data["EyeHeight"],0.2,'min')},
        {"Parameter":"Jitter (ns)","Datasheet":data["Jitter"],"JEDEC":0.16,"Status":status_color(data["Jitter"],0.16)},
    ])
    st.table(df_si)
    st.subheader("Reviewer Insights / Notes (Q&A)")
    st.markdown("Poor eye height/skew → data errors. Mitigation: layout optimization, SI simulation, terminations, and matched routing.")

# -------------------------------
# Tab 9 – DDR3/4/5 Context
# -------------------------------
with tabs[8]:
    st.subheader("What this tab is")
    st.write("Evolution of DDR standards and compatibility considerations.")
    st.subheader("Why it matters")
    st.write("Migration and controller design requires understanding differences.")
    df_ctx = pd.DataFrame([
        {"Type":"DDR3","Voltage":"1.5 V","Banks":8,"Primary Risk":"Power"},
        {"Type":"DDR4","Voltage":"1.2 V","Banks":16,"Primary Risk":"Timing"},
        {"Type":"DDR5","Voltage":"1.1 V","Banks":32,"Primary Risk":"SI/Power Noise"}
    ])
    st.table(df_ctx)
    st.subheader("Reviewer Insights / Notes (Q&A)")
    st.markdown("DDR4 improves over DDR3 with lower voltage, more banks, 8n prefetch. DDR5 further improves SI, speed, and on-die ECC. Migration requires timing and SI review.")

# -------------------------------
# Tab 10 – Final Review Summary
# -------------------------------
with tabs[9]:
    st.subheader("Final Review Summary & Mitigation")
    df_summary = pd.DataFrame([
        {"Domain":"DDR Basics","Status":"✅ PASS"},
        {"Domain":"Clock & Frequency","Status":status_color(data["tCK"],0.625)},
        {"Domain":"Addressing & Architecture","Status":"✅ PASS"},
        {"Domain":"Power & Voltages","Status":status_color(data["VDD"],1.2)},
        {"Domain":"AC Timing","Status":status_color(data["tAA"],13.75)},
        {"Domain":"Training","Status":"✅ PASS" if data["TrainingPass"] else "❌ FAIL"},
        {"Domain":"Refresh/Thermal","Status":"✅ PASS" if bandwidth_loss<=5 else "⚠️ MARGINAL" if bandwidth_loss<=6 else "❌ FAIL"},
        {"Domain":"Signal Integrity","Status":status_color(data["SignalMargin"],0.16)}
    ])
    st.table(df_summary)
    st.subheader("Reviewer Insights / Notes")
    st.markdown("""
- Golden parts pass all domains.
- Marginal parts show timing/thermal stress → monitor AC timing and refresh tax.
- Failure parts show clock, AC, SI, or thermal violations → mitigate with layout, cooling, CAS latency adjustment, and retest.
- Always validate with training logs and system-level stress tests.
- Final integration requires checking all boards and environmental conditions.
""")
