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

### Launcher Script
@echo off
setlocal

:: --- Configuration (Sanitized for Portability) ---
:: We use %~dp0 to refer to the folder where this batch file lives
set "SCRIPT_DIR=%~dp0"
set "VENV_PATH=%SCRIPT_DIR%.venv"
set "REQ_FILE=%SCRIPT_DIR%requirements.txt"
set "PY_SCRIPT=%SCRIPT_DIR%python_script_runner.py"

echo ====================================================
echo Initializing Finance Automation Hub
echo ====================================================

:: 1. Environment Check & Creation
:: This ensures every user has the exact same library versions
if not exist "%VENV_PATH%\Scripts\activate.bat" (
    echo [Step 1] Creating localized virtual environment...
    python -m venv "%VENV_PATH%" --upgrade-deps
)

:: 2. Activation
echo [Step 2] Activating Virtual Environment...
call "%VENV_PATH%\Scripts\activate.bat"

:: 3. Dependency Management
:: Upgrading pip and syncing from requirements.txt ensures the app never breaks
echo [Step 3] Syncing libraries from requirements.txt...
python -m pip install --upgrade pip
if exist "%REQ_FILE%" (
    python -m pip install -r "%REQ_FILE%"
)

:: 4. Launch Streamlit Hub
if exist "%PY_SCRIPT%" (
    echo [Step 4] Launching Streamlit UI...
    cd /d "%SCRIPT_DIR%"
    :: We use "python -m streamlit" for better compatibility across different installs
    python -m streamlit run "python_script_runner.py"
) else (
    echo [Error] Entry point "python_script_runner.py" not found!
    pause
)

:: 5. Cleanup on Close
call deactivate
echo Session Closed.
pause
