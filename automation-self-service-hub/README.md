# Self-Service Python Automation Hub (Streamlit)

## 📌 Project Overview
A centralized web-based Graphical User Interface (GUI) built to democratize data automation. This hub allows non-technical accounting and finance team members to execute complex Python pipelines (Bank Scraping, P&L Validation, etc.) without needing to interact with code or terminal environments.

## 🛠 The Technical Challenge
In many finance teams, "The Python Guy" becomes a single point of failure. If that person is on holiday, the automation stops.
* **Problem:** Users are intimidated by command lines and local Python installations.
* **Risk:** Version conflicts between different scripts' dependencies.
* **Requirement:** A secure, "one-click" environment for script execution with live logging.

## ⚙️ How it Works
1.  **UI Framework:** Developed using **Streamlit** for a modern, reactive web experience.
2.  **Orchestration Logic:** Uses the `subprocess` module to trigger scripts in a background thread.
3.  **Environment Isolation:** The hub is configured to run each script within its specific **Virtual Environment (venv)**, ensuring stability and version control.
4.  **Live Monitoring:** Captures `stdout` and `stderr` in real-time, displaying a "Terminal" view inside the browser so users can see the progress and any validation errors.



## 📊 Business Impact
* **Business Continuity:** Guaranteed 100% operational uptime for automation tasks during staff absences.
* **Democratization of Data:** Empowered 5+ non-technical staff members to leverage advanced data engineering tools independently.
* **Standardization:** Centralized all "shadow IT" scripts into a governed, audited interface.

## 🚀 Usage
```bash
# Install Streamlit
pip install streamlit

# Launch the Hub
streamlit run app.py
