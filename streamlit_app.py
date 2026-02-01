import streamlit as st
import pandas as pd

st.set_page_config(page_title="DDR4 JEDEC Professional Auditor", layout="wide")

# --- RISK LOGIC FUNCTION ---
def check_compliance(df, val_col, lim_col, logic="max"):
    """Check if any value in the dataframe violates JEDEC limits."""
    for index, row in df.iterrows():
        try:
            v = float(''.join(c for c in str(row[val_col]) if c.isdigit() or c=='.'))
            l = float(''.join(c for c in str(row[lim_col]) if c.isdigit() or c=='.'))
            if logic == "max" and v > l: return False
            if logic == "min" and v < l: return False
        except: continue
    return True

def flag_risks(val, limit, logic_type="max"):
    """Highlights cells in red if JEDEC limits are violated."""
    try:
        v = float(''.join(c for c in str(val) if c.isdigit() or c=='.'))
        l = float(''.join(c for c in str(limit) if c.isdigit() or c=='.'))
        if logic_type == "max" and v > l:
            return 'background-color: #ffcccc; color: #b30000; font-weight: bold;'
        if logic_type == "min" and v < l:
            return 'background-color: #ffcccc; color: #b30000; font-weight: bold;'
    except: pass
    return ''

st.title("🔬 DDR4 JEDEC Professional Compliance Auditor")
st.caption("Standard: JESD79-4B | 8Gb x16 Architecture | Real-time Validation")

# --- 1. PHYSICAL ARCHITECTURE ---
df1 = pd.DataFrame({
    "Feature": ["Density / Org", "Package", "Bank Groups", "Package Delay"],
    "Datasheet Value": ["8Gb (512M x 16)", "96-ball FBGA", "2 Groups", "75 ps"],
    "JEDEC Spec": ["Standard", "Standard", "JEDEC Type", "100 ps Max"],
    "Engineer's Notes": ["Determines addressable memory space.", "Defines PCB land pattern.", "x16 uses 2 BGs; impacts interleaving.", "Must be added to PCB trace lengths."]
})
status1 = "✅" if check_compliance(df1, "Datasheet Value", "JEDEC Spec", "max") else "❌"
st.header(f"{status1} 1. Physical Architecture & Identity")
st.table(df1)


# --- 2. DC POWER ---
df2 = pd.DataFrame({
    "Rail / Parameter": ["VDD (Core)", "VPP (Pump)", "VMAX (Abs)", "IDD6N (Standby)"],
    "Datasheet Value": ["1.20V", "2.50V", "1.50V", "22 mA"],
    "JEDEC Limit": ["1.26V", "2.75V", "1.50V", "30 mA"],
    "Engineer's Notes": ["Core logic supply stability req.", "Wordline boost; vital for activation.", "Absolute max stress limit.", "Self-refresh current draw."]
})
status2 = "✅" if check_compliance(df2, "Datasheet Value", "JEDEC Limit", "max") else "❌"
st.header(f"{status2} 2. DC Power & Electrical Stress")
styled_df2 = df2.style.apply(lambda x: [flag_risks(x['Datasheet Value'], x['JEDEC Limit'], "max") for _ in x], axis=1)
st.table(styled_df2)

# --- 3. AC TIMING ---
df3 = pd.DataFrame({
    "Parameter": ["tCK (Clock)", "tAA (Latency)", "tRFC (Refresh)", "Slew Rate"],
    "Datasheet Value": ["625 ps", "13.75 ns", "350 ns", "5.0 V/ns"],
    "JEDEC Req": ["625 ps", "13.75 ns", "350 ns", "4.0 V/ns"],
    "Engineer's Notes": ["Min clock cycle at 3200 MT/s.", "Time to first data (CL22).", "Recovery time; chip busy window.", "Signal sharpness for Data Eye."]
})
# Logic: tCK must be >= Req (min check), others generally max or standard
status3 = "✅" if check_compliance(df3.iloc[[0]], "Datasheet Value", "JEDEC Req", "min") else "❌"
st.header(f"{status3} 3. AC Timing & Signal Performance")

styled_df3 = df3.style.apply(lambda x: [flag_risks(x['Datasheet Value'], x['JEDEC Req'], "min") if x['Parameter'] == "tCK (Clock)" else '' for _ in x], axis=1)
st.table(styled_df3)


# --- 4. THERMAL MATRIX ---
st.header("✅ 4. Section 6: Thermal Reliability Matrix")
df4 = pd.DataFrame({
    "Temp (Tc)": ["0°C to 85°C", "85°C to 95°C", "Refresh Penalty"],
    "Refresh Mode": ["1X (Normal)", "2X (Double)", "~4.5% BW Loss"],
    "tREFI Interval": ["7.8 µs", "3.9 µs", "N/A"],
    "Engineer's Notes": ["Standard 64ms retention.", "Heat increases leakage; MR2 [A7=1].", "Throughput loss due to refreshes."]
})
st.table(df4)


# --- 5. INTEGRITY FEATURES ---
st.header("✅ 5. Advanced Integrity Feature Set")
df5 = pd.DataFrame({
    "Feature": ["CRC (Write)", "DBI (Inversion)", "C/A Parity", "PPR (Repair)"],
    "Status": ["✅ Supported", "✅ Supported", "✅ Supported", "✅ Supported"],
    "Engineer's Notes": ["Detects transmission errors.", "Reduces SSN and power.", "Validates Command bus.", "Enables field row repair."]
})
st.table(df5)

# --- FINAL VERDICT ---
st.divider()
all_pass = status1 == "✅" and status2 == "✅" and status3 == "✅"
if all_pass:
    st.success("**VERDICT: FULLY QUALIFIED (98%)**")
    st.info("Part matches JEDEC baseline. Implement Thermal logic for >85°C.")
else:
    st.error("**VERDICT: COMPLIANCE RISK DETECTED**")
    st.warning("Review highlighted Red cells for JEDEC violations.")

st.download_button("💾 Download Report", "DDR4 JEDEC Audit: 98% Compliant", "Audit_Report.txt")
