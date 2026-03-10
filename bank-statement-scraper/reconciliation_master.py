# -*- coding: utf-8 -*-
"""
Banking Reconciliation Master Orchestrator

Description:
This script consolidates processed balance data from multiple global financial 
institutions into a master SAGE/ERP reconciliation workbook. It automates 
file versioning, data aggregation, and Excel-based reporting via xlwings.

Key Features:
- Automated T-1 business day folder and file discovery.
- Multi-bank data aggregation (BNP, HSBC, JPM, DB, etc.).
- Dynamic Excel cell mapping and formatting (Highlighting & Hyperlinking).
- COM-based macro execution for final ledger balancing.

Author: David Zadera (Portfolio Version)
"""

import os
import shutil
import time
import pandas as pd
import xlwings as xw
from pandas.tseries.offsets import BDay

# --- CONFIGURATION ---
# Define root paths as environment variables for portability
ROOT_DIR = os.getenv("FINANCE_RECON_ROOT", "data/banking_reconciliations/")
TEMPLATE_NAME = "Master_Bank_Rec_Template.xlsm"

def get_target_paths():
    """Calculates source and destination paths based on business days."""
    target_date = pd.Timestamp.today().normalize() - BDay(1)
    source_date = target_date - BDay(1)

    def format_path(dt):
        return os.path.join(ROOT_DIR, str(dt.year), dt.strftime("%m.%y"))

    src_folder = format_path(source_date)
    dst_folder = format_path(target_date)
    
    # Generic file naming convention for portfolio
    fmt = "%Y.%m.%d"
    src_file = f"Bank_Rec_Ledger_{source_date.strftime(fmt)}.xlsm"
    dst_file = f"Bank_Rec_Ledger_{target_date.strftime(fmt)}.xlsm"

    return target_date, os.path.join(src_folder, src_file), os.path.join(dst_folder, dst_file), dst_folder

def load_bank_balances(base_folder, target_date):
    """
    Scans subdirectories for individual bank balance exports and 
    aggregates them into a single master DataFrame.
    """
    date_suffix = target_date.strftime('%d%m%y')
    
    # List of bank modules to aggregate
    banks = ["INTERNAL", "HSBC", "JPM", "BNP", "DB", "MASHREQ", "RAIFFEISEN"]
    all_dfs = []

    for bank in banks:
        # Construct path to the specific bank's processed folder
        bank_subfolder = os.path.join(base_folder, f"{bank}_processed")
        file_path = os.path.join(bank_subfolder, f"balances_{bank}_{date_suffix}.xlsx")
        
        if os.path.exists(file_path):
            try:
                df = pd.read_excel(file_path, sheet_name="Summary", 
                                  usecols=["PDF File", "Account Number", "Transaction Count", "Final Balance"])
                df["Account Number"] = df["Account Number"].astype(str)
                all_dfs.append(df)
                print(f"Loaded: {bank} records.")
            except Exception as e:
                print(f"Error reading {bank}: {e}")
    
    if not all_dfs:
        return pd.DataFrame()

    master_df = pd.concat(all_dfs, ignore_index=True)
    master_df.drop_duplicates(subset="Account Number", inplace=True)
    return master_df

def update_excel_ledger(ledger_path, target_date, balances_df):
    """Orchestrates the Excel updates using xlwings."""
    app = xw.App(visible=False)
    try:
        wb = app.books.open(ledger_path)
        ws = wb.sheets["Bank Rec"]

        # 1. Update Header Dates
        next_bday = (target_date + BDay(1)).strftime("%Y/%m/%d")
        curr_bday = target_date.strftime("%Y/%m/%d")
        
        ws.range("B1").value = next_bday
        ws.range("B3").value = curr_bday

        # 2. Map Balances to Ledger Rows
        # Create a lookup map for O(1) efficiency
        balances_map = balances_df.set_index('Account Number').T.to_dict('list')

        # Iterate through ledger rows (Example: Rows 11 to 81)
        for row in range(11, 81):
            acc_cell = ws.range(f"D{row}").value
            if acc_cell:
                acc_id = str(int(acc_cell)) if isinstance(acc_cell, (int, float)) else str(acc_cell)
                
                # Reset formatting
                ws.range(f"J{row}:O{row}").color = None
                
                if acc_id in balances_map:
                    pdf_file, count, balance = balances_map[acc_id]
                    
                    # Update Balance and Count
                    ws.range(f"J{row}").value = balance
                    ws.range(f"O{row}").value = count
                    
                    # Apply "Visual Cue" (Yellow highlight for automated updates)
                    ws.range(f"J{row},O{row}").color = (255, 255, 0)
                    
                    # Insert Hyperlink to Audit Trail (PDF)
                    ws.range(f"T{row}").add_hyperlink(pdf_file, "View Source PDF")

        # 3. Finalize
        wb.save()
        try:
            # Trigger VBA logic for final reconciliation checks
            wb.macro("refreshbalances")()
            wb.save()
            print("VBA refresh successful.")
        except Exception as e:
            print(f"VBA Macro execution skipped or failed: {e}")
            
        wb.close()
    finally:
        app.quit()

def main():
    target_date, src_path, dst_path, dst_folder = get_target_paths()

    # Step 1: Version Control (Copy Yesterdays Ledger to Today)
    if os.path.exists(src_path):
        os.makedirs(os.path.dirname(dst_path), exist_ok=True)
        shutil.copy2(src_path, dst_path)
        print(f"New ledger version created for {target_date.date()}")
    else:
        print(f"Source ledger not found: {src_path}")
        return

    # Step 2: Aggregate Processed Bank Data
    balances_df = load_bank_balances(dst_folder, target_date)
    
    if not balances_df.empty:
        # Save a reference copy for audit purposes
        audit_path = os.path.join(dst_folder, "All_Statement_Balances_Ref.xlsx")
        balances_df.to_excel(audit_path, index=False)
        
        # Step 3: Write to Excel
        update_excel_ledger(dst_path, target_date, balances_df)
    else:
        print("No balances found to process.")

if __name__ == "__main__":
    main()
