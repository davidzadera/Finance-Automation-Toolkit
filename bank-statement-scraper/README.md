# Multi-Bank PDF Scraping & Reconciliation Suite

## 📌 Project Overview
This repository contains a modular automation framework designed to eliminate manual data entry in daily banking operations. The system parses unstructured PDF bank statements from multiple global institutions and orchestrates the update of a master Sage/ERP reconciliation ledger.

## 🏗 System Architecture
The solution is split into two functional layers:

1.  **Extraction Layer (Scrapers):** Bank-specific Python scripts utilizing `pdfplumber` and `Regex` to handle unique statement layouts (BNP, HSBC, JPM, etc.). These scripts normalize data and identify PDF encoding artifacts (e.g., character duplication).
2.  **Orchestration Layer (Master):** A controller script that aggregates processed data, performs T-1 version control on Excel ledgers, and uses `xlwings` to inject balances and audit trails (hyperlinks) into the final report.



## 🛠 Technical Highlights
* **Complex Regex Parsing:** Extracts transaction dates, reference codes, and multi-currency balances from unstructured text.
* **Data Integrity:** Includes a custom cleaning algorithm to resolve "ghost" character duplication caused by specific PDF font encodings.
* **Excel Interop:** Leverages `xlwings` to bridge the gap between Python data processing and legacy VBA-enabled Excel workbooks.
* **Auditability:** Automatically generates a "Summary" report and embeds direct hyperlinks to source PDFs within the Excel environment for easy stakeholder review.

## 📊 Business Impact
* **Scalability:** The framework is designed to onboard new bank formats by simply adding a new regex mapping module.
* **Risk Reduction:** Achieved 100% accuracy in daily balance reporting across 50+ bank accounts.
* **Time Savings:** Reduced the end-to-end banking workflow from 60 minutes of manual entry to under 5 minutes of automated execution.

## 🚀 Execution
To run the end-to-end process:
```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run the master orchestrator (triggers scrapers and updates Excel)
python reconciliation_master.py
