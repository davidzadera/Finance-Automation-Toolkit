import streamlit as st

# Set page configuration for a professional look
st.set_page_config(page_title="Finance Automation Hub", page_icon="📈", layout="wide")

# Sidebar Branding
st.sidebar.title("Automation Hub")
st.sidebar.markdown("---")
st.sidebar.info("Select a functional module below to access specific automation tools.")

# Define the Navigation Structure
# These point to the individual "Runner" files in the same directory
bank_rec_page = st.Page(
    "python_script_runner_bankrec.py", 
    title="Banking & Treasury", 
    icon="🏦"
)
pl_checks_page = st.Page(
    "python_script_runner_plchecks.py", 
    icon="📊",
    title="P&L & Intercompany"
)
other_scripts_page = st.Page(
    "python_script_runner_other.py", 
    title="Specialized Utilities", 
    icon="🛠️"
)

# Initialize Navigation
pg = st.navigation({
    "Core Workflows": [bank_rec_page, pl_checks_page],
    "Tools": [other_scripts_page]
})

# Run the selected page
pg.run()
