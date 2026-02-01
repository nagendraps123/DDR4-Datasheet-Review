# 🔬 DDR4 JEDEC Professional Compliance Auditor

### 🚀 Project Overview
This tool automates the auditing of memory datasheets against the **JESD79-4B JEDEC Standard**. It uses AI-driven text extraction to identify the **Part Number** and validates architecture, power, timing, and thermal reliability to ensure system-level stability.

### 🔬 The 5-Section Audit Framework
Every audit generates a professional report covering:
1. **Architecture**: Package delays and bank group configurations.
2. **DC Power**: Core voltage ($V_{DD}$) and boost voltage ($V_{PP}$) tolerances.
3. **AC Timing**: Speed-bin verification ($t_{CK}$, $t_{AA}$, $t_{RFC}$).
4. **Thermal Reliability**: Refresh rate scaling (1X/2X) for high-temperature operation.
5. **Advanced Integrity**: Feature support for CRC, DBI, and Parity.

### 📥 How to Use
1. **Open the App**: Click the link in the repository description.
2. **Input Project Info**: Enter the "Hardware Project Name" for document control.
3. **Upload Datasheet**: Upload the manufacturer's PDF (Samsung, Micron, SK Hynix, etc.).
4. **Review Verdict**: Analyze the 4-point mitigation plan (BIOS, PCB, Signal, and Reliability).
5. **Download PDF**: Export the final report. 

> **Note**: The **Part Number** is automatically tracked in every page header and footer of the generated PDF.



### 🛠 Technical Mitigation Requirements
The auditor flags specific actions based on compliance:
* **BIOS**: Automatic enforcement of 2X Refresh scaling for $T_{case} > 85°C$.
* **PCB**: Compensation for internal silicon-to-ball delays (e.g., 75ps).
* **Signal**: Mandatory DBI enablement to suppress switching noise.
* **Reliability**: CRC activation for mission-critical environments.
