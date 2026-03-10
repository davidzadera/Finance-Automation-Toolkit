import streamlit as st
from datetime import datetime
from pandas.tseries.offsets import BDay
import re
import subprocess
import os
import sys

# --- PORTABLE PATH LOGIC ---
# Instead of os.getlogin(), we look for the venv relative to this script
# this matches the structure created by your .bat file
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# Points to the .venv folder in your project root
VENV_PYTHON = os.path.join(BASE_DIR, ".venv", "Scripts", "python.exe")

# Fallback to sys.executable if running outside the intended .bat structure
if not os.path.exists(VENV_PYTHON):
    VENV_PYTHON = sys.executable

# Define the script configurations
# Note: Internal names and paths have been generalized for portfolio purposes
script_args = {
    "Daily Extraction - BNP": {
        "fields": {
            "date": {
                "description": "Extraction Date (YYYY-MM-DD):",
                "default": (datetime.now() - BDay(1)).strftime("%Y-%m-%d"),
                "arg_name": "--date",
                "validate": lambda x: re.match(r"^\d{4}-\d{2}-\d{2}$", x) is not None,
                "error_message": "Date must be in YYYY-MM-DD format."
            }
        },
        "description": "Parses unstructured PDF statements for BNP Paribas and standardizes transaction data.",
        "script_name": "bank_scraper_bnp.py"
    },
    "Daily Extraction - HSBC": {
        "fields": {},
        "description": "Automated data extraction and normalization for HSBC global accounts.",
        "script_name": "bank_scraper_hsbc.py"
    },
    "Master Ledger Update": {
        "fields": {},
        "description": "Orchestrates the consolidation of all individual bank extracts into the Master Reconciliation Workbook.",
        "script_name": "reconciliation_master.py"
    }
}

# --- UI STYLING ---
st.markdown("""
    <style>
    .reportview-container .main .block-container { padding-top: 2rem; }
    .stAppDeployButton { visibility: hidden; }
    .output-label { font-size: 20px; font-weight: bold; color: #1E88E5; }
    </style>
    """, unsafe_allow_html=True)

# --- SIDEBAR ---
st.sidebar.title("Navigation & Help")
st.sidebar.info("""
**User Guide:**
1. **Select Module**: Choose a bank or master process.
2. **Parameters**: Enter required dates (defaults to T-1).
3. **Execute**: Monitor live logs in the output panel.
""")

# --- LOGIC FUNCTIONS ---
def get_script_arguments(script_option):
    fields = script_args[script_option].get("fields", {})
    args = {}
    for field, details in fields.items():
        val = st.text_input(details["description"], details["default"])
        if not details["validate"](val):
            st.error(details["error_message"])
            return None
        args[details["arg_name"]] = val
    return args

def run_automation(script_option, args_dict):
    script_name = script_args[script_option]["script_name"]
    # We assume 'scripts/' folder holds the workers
    script_path = os.path.join(BASE_DIR, "scripts", script_name)
    
    # Construct command: [python, script, --arg=val]
    command = [VENV_PYTHON, script_path]
    for arg, val in args_dict.items():
        command.append(f"{arg}={val}")

    try:
        process = subprocess.run(command, text=True, capture_output=True)
        return process.stdout, process.stderr
    except Exception as e:
        return None, f"System Error: {str(e)}"

# --- MAIN INTERFACE ---
st.title("🏦 Banking & Treasury Automation")
st.divider()

selection = st.selectbox("Select Automation Module", list(script_args.keys()))

# Special Warnings
if "Master" in selection:
    st.warning("⚠️ Warning: Executing this will overwrite the active Master Reconciliation Ledger.")

with st.expander("Process Details", expanded=True):
    st.write(script_args[selection]["description"])

# Gather Inputs
current_args = get_script_arguments(selection)

if st.button("🚀 Execute Pipeline"):
    if current_args is not None:
        with st.status(f"Running {selection}...", expanded=True) as status:
            stdout, stderr = run_automation(selection, current_args)
            
            if stderr:
                st.error("Errors/Warnings detected during execution.")
                st.code(stderr)
            
            if stdout:
                st.success("Execution Complete.")
                st.code(stdout)
            status.update(label="Process Finished", state="complete")
