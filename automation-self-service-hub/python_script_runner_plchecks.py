import streamlit as st
from datetime import datetime
from pandas.tseries.offsets import BDay
import re
import subprocess
import os
import sys

# --- PORTABLE VENV CONFIG ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
VENV_PYTHON = os.path.join(BASE_DIR, ".venv", "Scripts", "python.exe")

if not os.path.exists(VENV_PYTHON):
    VENV_PYTHON = sys.executable

# Define the script configurations
# Note: Entity codes (Entity_A, Entity_B) represent intercompany pairs
script_args = {
    "Entity_A to Entity_B: Book P&L Recon": {
        "fields": {
            "date": {
                "description": "Position Date (YYYY-MM-DD):",
                "validate": lambda x: re.match(r'^\d{4}-\d{2}-\d{2}$', x) is not None,
                "default": (datetime.today().date() - BDay(2)).strftime('%Y-%m-%d'),
                "arg_name": "--date",
                "error_message": "Invalid date format. Please use YYYY-MM-DD."
            }
        },
        "description": "Executes the Book P&L reconciliation between Entity_A and Entity_B. Automates email distribution post-20th of the month.",
        "script_name": "pnl_book_recon_ab.py"
    },
    "Entity_C to Entity_B: Invoice Reconciliation": {
        "fields": {
            "date": {
                "description": "Position Date (YYYY-MM-DD):",
                "validate": lambda x: re.match(r'^\d{4}-\d{2}-\d{2}$', x) is not None,
                "default": (datetime.today().date() - BDay(2)).strftime('%Y-%m-%d'),
                "arg_name": "--date",
                "error_message": "Invalid date format. Please use YYYY-MM-DD."
            }
        },
        "description": "Cross-references 'New Ana' records against processed invoices. Requires latest Alteryx posting tables as a prerequisite.",
        "script_name": "invoice_recon_cb.py"
    },
    "Global Group: Consolidated NA Recon": {
        "fields": {
            "date": {
                "description": "Position Date (YYYY-MM-DD):",
                "validate": lambda x: re.match(r'^\d{4}-\d{2}-\d{2}$', x) is not None,
                "default": (datetime.today().date() - BDay(2)).strftime('%Y-%m-%d'),
                "arg_name": "--date",
                "error_message": "Invalid date format. Please use YYYY-MM-DD."
            }
        },
        "description": "Aggregates P&L data across all regional subsidiaries to identify intra-group variance.",
        "script_name": "global_na_recon.py"
    }
}

# --- UI STYLING ---
st.markdown("""
    <style>
    .small-font { font-size:22px !important; font-weight: bold; color: #2E7D32; }
    .stAppDeployButton { visibility: hidden; }
    </style>
    """, unsafe_allow_html=True)

# --- SIDEBAR ---
st.sidebar.title("P&L Workflow Guide")
st.sidebar.warning("""
**Prerequisite:**
Ensure Alteryx Posting Tables have been updated before running Invoice Reconciliations to ensure data freshness.
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

def execute_logic(script_option, arguments):
    script_config = script_args[script_option]
    script_path = os.path.join(BASE_DIR, "scripts", script_config["script_name"])
    
    command = [VENV_PYTHON, script_path] + [f"{arg}={val}" for arg, val in arguments.items()]

    try:
        result = subprocess.run(command, text=True, capture_output=True)
        return result.stdout, result.stderr
    except Exception as e:
        return None, f"Execution Failure: {str(e)}"

# --- INTERFACE ---
st.title("📊 P&L & Intercompany Validation")
st.divider()

selection = st.selectbox("Select Reconciliation Module", list(script_args.keys()))

with st.container(border=True):
    st.info(script_args[selection]["description"])

inputs = get_script_arguments(selection)

if st.button("🚀 Run Reconciliation"):
    if inputs is not None:
        with st.spinner(f"Processing {selection}..."):
            stdout, stderr = execute_logic(selection, inputs)
            
            st.markdown('<p class="small-font">Process Logs:</p>', unsafe_allow_html=True)
            if stdout:
                st.code(stdout)
            else:
                st.write("No standard output generated.")
                
            if stderr:
                st.error("Technical Warnings/Errors:")
                st.code(stderr)
