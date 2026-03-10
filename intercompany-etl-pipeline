# Intercompany P&L & Invoice ETL Pipeline

## 📌 Overview
This project automates the validation of intercompany P&L and invoices across 6 global entities. It transitions the finance team from manual line-by-line verification to a **"Management by Exception"** workflow.

## 🛠 The Technical Challenge
Intercompany reconciliations in trading are complex due to:
* High volume of daily transactions across different time zones.
* Data fragmentation between analytical tools (New Ana) and accounting ledgers.
* The need for 100% accuracy to prevent month-end reporting delays.

## ⚙️ How it Works
1. **Extraction:** The pipeline uses **Power Query** to pull live data via API from the internal analytical tool into standardized Excel templates.
2. **Orchestration:** A Python script (`main.py`) acts as the "Controller," triggering simultaneous background refreshes of all entity templates using `xlwings`.
3. **Transformation & Validation:** Using **Pandas**, the script performs vectorized logic checks to identify P&L mismatches and missing invoices.
4. **Automated Reporting:** The script generates a summary status (Pass/Fail) and dispatches automated email alerts via `win32com`.



## 📊 Business Impact
* **Efficiency:** Reduced manual reconciliation time by **10+ hours per month**.
* **Risk Mitigation:** Guaranteed 100% daily coverage of all intercompany flows.
* **Scalability:** The modular design allows for new entities to be added with minimal configuration changes.

## 🚀 Usage
```bash
# Install dependencies
pip install -r requirements.txt

# Run the pipeline
python main.py
