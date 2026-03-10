# Finance Automation & Data Engineering Toolkit
### Created by David Zadera

This repository contains a collection of production-grade automation tools developed to transform traditional accounting workflows into scalable, exception-based systems within the commodity trading sector.

## 🚀 Key Projects

### 1. Intercompany Reconciliation Pipeline (ETL)
* **The Problem:** Manual P&L and invoice validation across 6 global entities was time-consuming and prone to human error.
* **The Solution:** A Python-based ETL pipeline that pulls API data (New Ana), performs discrepancy logic in Pandas, and generates automated stakeholder reports.
* **Impact:** Saved 10+ hours/month and ensured 100% daily coverage.

### 2. Automated Multi-Bank PDF Scraper
* **The Problem:** High-volume daily bank statements from multiple institutions required manual entry.
* **The Solution:** A modular framework using `pdfplumber` and Regex to parse unstructured data into standardized financial DataFrames.
* **Impact:** Scaled operations to handle new entities without increasing headcount.

### 3. Self-Service Automation Hub (Streamlit)
* **The Problem:** Non-technical team members were dependent on local script execution.
* **The Solution:** A web-based GUI built with Streamlit and a Subprocess orchestration engine.
* **Impact:** Guaranteed business continuity and process resilience during staff absences.

## 🛠 Tech Stack
* **Languages:** Python (Pandas, xlwings, Streamlit), Oracle SQL.
* **Tools:** Power BI, Power Automate, Alteryx.
* **Finance Logic:** P&L Attribution, Intercompany Reconciliations, Futures & Swaps Control.

---
*Note: All code samples have been sanitized to remove proprietary company data and server credentials.*
