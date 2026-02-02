import streamlit as st
import pandas as pd
from fpdf import FPDF
from datetime import datetime

# --- 1. PDF CLASS WITH HEADER/FOOTER ---
class DRAM_Report(FPDF):
    def __init__(self, part_number):
        super().__init__()
        self.part_number = part_number

    def header(self):
        self.set_font("Arial", 'B', 10)
        self.cell(0, 10, f"DDR Compliance Audit | Part No: {self.part_number}", 0, 1, 'R')
        self.line(10, 18, 200, 18)

    def footer(self):
        self.set_y(-15)
        self.set_font("Arial", 'I', 8)
        self.cell(0, 10, f"Page {self.page_no()} | Part Number: {self.part_number}", 0, 0, 'C')

# --- 2. GLOBAL AUDIT DATA ---
AUDIT_SECTIONS = {
    "1. Physical Architecture": {
        "intro": "Validates the silicon-to-package interface and signal path matching (Pkg Delay) to ensure timing skew remains within JEDEC boundaries.",
        "df": pd.DataFrame({
            "Feature": ["Density", "Package", "Bank Groups", "Pkg Delay"],
            "Value": ["8Gb (512Mx16)", "96-FBGA", "2 Groups", "75 ps"],
            "Spec": ["JESD79-4 Compliant", "Standard", "x16 Type", "100ps Max"],
            "Significance": [
                "Address mapping; affects Row/Column/Bank bit-ordering for controller addressing.",
                "Ball pitch and layout; dictates the escape routing and PCB impedance control requirements.",
                "Enables Bank Group (BG) interleaving to satisfy tCCD_S timing constraints for high bandwidth.",
                "Silicon-to-package trace length; exceeding 100ps breaks signal fly-by topology synchronicity."
            ]
        })
    },
    "2. DC Power": {
        "intro": "Analyzes electrical rails to ensure the DUT operates within the safe operating area (SOA) defined by JEDEC DC specifications.",
        "df": pd.DataFrame({
            "Feature": ["VDD", "VPP", "VMAX", "IDD6N"],
            "Value": ["1.20V", "2.50V", "1.50V", "22 mA"],
            "Spec": ["1.14V - 1.26V", "2.375V - 2.75V", "1.50V Max", "30mA Max"],
            "Significance": [
                "Core supply; rail noise exceeding +/- 60mV triggers internal logic state meta-stability.",
                "Wordline boost supply; must remain above 2.375V to ensure overdrive of memory cell access transistors.",
                "Absolute maximum rating; exceeding this point causes irreversible gate-oxide dielectric breakdown.",
                "Self-refresh current; critical for verifying JEDEC IDD/IPP low-power standby compliance."
            ]
        })
    },
    "3. Timing Parameters": {
        "intro": "Critical AC timing audit. These parameters define the window of validity for data strobes (DQS) and command signals.",
        "df": pd.DataFrame({
            "Feature": ["tCK (avg)", "tCL", "tRCD", "tRP"],
            "Value": ["0.938 ns", "16 cycles", "16 cycles", "16 cycles"],
            "Spec": ["0.937ns Min", "CL=16", "tRCD=16", "tRP=16"],
            "Significance": [
                "Average Clock Period; the fundamental frequency reference for all high-speed signaling (1066MHz).",
                "CAS Latency; the delay from Read command to valid data burst; critical for memory controller scheduler.",
                "RAS to CAS delay; timing required for row activation before sensing can occur.",
                "Row Precharge; minimum time to close a bank to allow the bitlines to equalize for the next access."
            ]
        })
    },
    "4. Thermal & Environmental": {
        "intro": "Evaluates the device's ability to maintain data integrity across the JEDEC industrial and commercial temperature grades.",
        "df": pd.DataFrame({
            "Feature": ["T-Oper", "T-Storage", "Refresh Rate", "Thermal Sensor"],
            "Value": ["0 to 95 C", "-55 to 100 C", "64ms @ <85C", "Integrated"],
            "Spec": ["0 to 95 C", "Standard", "32ms @ >85C", "JESD21-C Compliant"],
            "Significance": [
                "Standard JEDEC operating range; T-Case above 95C accelerates electron leakage beyond refresh recovery.",
                "Storage limits; defines the thermal budget before permanent silicon aging or data retention failure.",
                "tREFI requirement; must be doubled (3.9us) at elevated temperatures to counter bitline charge decay.",
                "Integrated Sensor; required for 'Thermal Throttling' and auto-adjustment of refresh cycles."
            ]
        })
    },
    "5. Command & Address": {
        "intro": "Verifies the command bus integrity protocols, including parity and retry logic to prevent system-level hangs.",
        "df": pd.DataFrame({
            "Feature": ["C/A Latency", "CA Parity", "CRC Error", "DBI"],
            "Value": ["Disabled", "Enabled", "Auto-Retry", "Enabled"],
            "Spec": ["Optional", "Required", "Required", "Optional"],
            "Significance": [
                "Command/Address latency; disabling reduces controller complexity but may impact timing closure.",
                "Parity check on command/address bus; mandatory for JEDEC DDR4 to detect single-bit errors.",
                "Cyclic Redundancy Check; ensures burst-level integrity and triggers auto-retry on failure.",
                "Data Bus Inversion; reduces simultaneous switching noise by inverting high-density data patterns."
            ]
        })
    }
}

# --- 3. STREAMLIT APP ---
st.title("DDR Compliance Audit Report Generator")

part_number = st.text_input("Enter Part Number:", "ABC123")

# Display sections interactively
for section, content in AUDIT_SECTIONS.items():
    st.subheader(section)
    st.write(content["intro"])
    st.dataframe(content["df"])

# Generate PDF
if st.button("Generate PDF Report"):
    pdf = DRAM_Report(part_number=part_number)
    pdf.add_page()

    for section, content in AUDIT_SECTIONS.items():
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(0, 10, section, ln=True)
        pdf.set_font("Arial", '', 10)
        pdf.multi_cell(0, 10, content["intro"])
        pdf.ln(2)

        df = content["df"]
        pdf.set_font("Arial", '', 9)
        col_widths = [40, 40, 40, 70]
        headers = ["Feature", "Value", "Spec", "Significance"]

        # Table header
        for i, h in enumerate(headers):
            pdf.cell(col_widths[i], 8, h, 1)
        pdf.ln()

        # Table rows
        for _, row in df.iterrows():
            pdf.cell(col_widths[0], 8, str(row["Feature"]), 1)
            pdf.cell(col_widths[1], 8, str(row["Value"]), 1)
            pdf.cell(col_widths[2], 8, str(row["Spec"]), 1)
            pdf.cell(col_widths[3], 8, str(row["Significance"]), 1)
            pdf.ln()
        pdf.ln(5)

    # Save to bytes
    pdf_bytes = pdf.output(dest='S').encode('latin-1')
    st.download_button(
        label="Download PDF",
        data=pdf_bytes,
        file_name=f"DDR_Audit_{part_number}_{datetime.now().strftime('%Y%m%d')}.pdf",
        mime="application/pdf"
    )
