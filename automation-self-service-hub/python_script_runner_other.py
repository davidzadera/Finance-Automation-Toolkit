import streamlit as st
from datetime import datetime
from pandas.tseries.offsets import BDay
import re
import subprocess
import os
import sys

# --- PORTABLE VENV CONFIG ---
# Automatically detects the virtual environment relative to this file
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
VENV_PYTHON = os.path.join(BASE_DIR, ".venv", "Scripts", "python.exe")

# Fallback for local development/testing
if not os.path.exists(VENV_PYTHON):
    VENV_PYTHON = sys.executable

# Define the script configurations
script_args = {
    "Generate Posting File (BNP)": {
        "fields": {
            "date": {
                "description": "Position Date (YYYY-MM-DD):",
                "validate": lambda x: re.match(r'^\d{4}-\d{2}-\d{2}$', x) is not None,
                "default": (datetime.today().date() - BDay(1)).strftime('%Y-%m-%d'),
                "arg_name": "--date",
                "error_message": "Invalid date format. Please use YYYY-MM-DD."
            }
        },
        "description": "Automates the transfer of daily transaction data from raw CSV exports to standardized accounting templates.",
        "script_name": "bnp_posting_generator.py"
    },
    "Update Settlement & Market Prices": {
        "fields": {},
        "description": "Synchronizes settlement prices, IODA swaps/futures, and book valuations across internal control files.",
        "script_name": "run_market_prices.py"
    },
    "System Health & Script Checker": {
        "fields": {
            "date": {
                "description": "Date to Check (YYYY-MM-DD):",
                "validate": lambda x: re.match(r'^\d{4}-\d{2}-\d{2}$', x) is not None,
                "default": (datetime.today().date()).strftime('%Y-%m-%d'),
                "arg_name": "--date",
                "error_message": "Invalid date format. Please use YYYY-MM-DD."
            }
        },
        "description": "Monitors directory integrity for missing daily reports and dispatches status alerts to the team.",
        "script_name": "system_integrity_check.py"
    },
    "Web Driver Maintenance": {
        "fields": {},
        "description": "Automated utility to verify and update Selenium Chromedriver versions to maintain scraper stability.",
        "script_name": "driver_maintenance.py"
    }
}

# --- UI STYLING ---
st.markdown("""
    <style>
    .small-font { font-size:20px !important; font-weight: bold; }
    .stAppDeployButton { visibility: hidden; }
    </style>
    """, unsafe_allow_html=True)

# --- SIDEBAR ---
st.sidebar.title("Automation Hub Help")
st.sidebar.info("""
**Utility Module:**
Select a tool from the dropdown to view its description and required parameters. 
Execution logs will appear at the bottom of the page.
""")

# --- LOGIC ---
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

def run_script(script_option, arguments):
    script_config = script_args[script_option]
    # Pointing to the 'scripts' subdirectory for the workers
    script_path = os.path.join(BASE_DIR, "scripts", script_config["script_name"])
    
    command = [VENV_PYTHON, script_path] + [f"{arg}={val}" for arg, val in arguments.items()]

    try:
        result = subprocess.run(command, text=True, capture_output=True)
        return result.stdout, result.stderr
    except Exception as e:
        return None, f"Runtime Error: {str(e)}"

# --- INTERFACE ---
st.title("🛠️ specialized Utilities")
st.divider()

option = st.selectbox("Select Utility Tool", list(script_args.keys()))

with st.container(border=True):
    st.markdown("**Description:**")
    st.write(script_args[option]["description"])

inputs = get_script_arguments(option)

if st.button("▶️ Run Utility"):
    if inputs is not None:
        with st.status(f"Executing {option}...", expanded=True):
            stdout, stderr = run_script(option, inputs)
            
            st.markdown('<p class="small-font">Standard Output:</p>', unsafe_allow_html=True)
            st.code(stdout if stdout else "Process completed with no console output.")
            
            if stderr:
                st.markdown('<p class="small-font" style="color:orange;">Logs/Warnings:</p>', unsafe_allow_html=True)
                st.code(stderr)
