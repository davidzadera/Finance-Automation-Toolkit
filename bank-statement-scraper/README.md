# Automated Multi-Bank PDF Reconciliation Suite

## 📌 Overview
An intelligent data extraction framework designed to parse unstructured PDF bank statements from global financial institutions (BNP Paribas, HSBC, Deutsche Bank) into standardized, analysis-ready DataFrames.

## 🛠 The Technical Challenge
Bank statements are notoriously difficult to automate because:
* Each bank uses a different layout and table structure.
* PDF data is "unstructured" (text is often just floating coordinates rather than a table).
* Manual entry of high-volume daily cash flows is a significant source of operational risk.

## ⚙️ How it Works
1. **Ingestion:** The script monitors a source directory for new PDF statements.
2. **Bank Identification:** Using metadata and header detection, the system identifies which bank the statement belongs to and selects the corresponding parsing logic.
3. **Extraction (pdfplumber + Regex):**
    * Uses `pdfplumber` to locate table boundaries.
    * Applies **Regular Expressions (Regex)** to capture dates, transaction descriptions, and amounts, regardless of shifting text positions.
4. **Standardization:** All extracted data is mapped to a unified schema (Date, Value, Currency, Reference, Bank) using **Pandas**.



## 📊 Business Impact
* **Headcount Efficiency:** Enabled the team to absorb new entity volumes without adding additional staff.
* **Accuracy:** Eliminated manual data entry errors, ensuring 100% alignment with bank balances.
* **Speed:** Reduced daily processing time from ~60 minutes to under 5 minutes.

## 🚀 Usage
```bash
# Install dependencies
pip install -r requirements.txt

# Run the scraper
python scraper_engine.py
