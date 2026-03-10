# -*- coding: utf-8 -*-
"""
Automated Inter-Entity Reconciliation Pipeline

Description:
This script automates the reconciliation between analytical trading data and 
accounting ledgers. It performs data extraction via a template-based approach,
executes logic-driven macros, and dispatches exception reports to stakeholders.

Author: David Zadera (Portfolio Version)
"""

import os
import shutil
import argparse
import time as tm
from datetime import datetime
import pandas as pd
import xlwings as xw
import win32com.client
from pandas.tseries.offsets import CustomBusinessDay

# --- CONFIGURATION (Move these to environment variables in production) ---
BASE_DIR = os.getenv("FINANCE_DATA_ROOT", "data/reconciliations/")
TEMPLATE_DIR = os.getenv("FINANCE_TEMPLATES", "templates/")
RECIPIENT_EMAIL = os.getenv("RECON_EMAIL", "stakeholder@example.com")
BACKUP_DIR = os.getenv("BACKUP_PATH", "data/backup/")

def get_bank_holidays():
    """Fetch public bank holidays to accurately calculate business days."""
    try:
        # Using UK Government API as a reliable public source
        bank_holidays = pd.read_json('https://www.gov.uk/bank-holidays.json')
        holidays = []
        for details in bank_holidays['england-and-wales']['events']:
            holidays.append(pd.to_datetime(details['date']))
        return holidays
    except Exception as e:
        print(f"Warning: Could not fetch holidays, defaulting to standard weekends. {e}")
        return []

def run_reconciliation(position_date):
    """
    Main execution logic for data refresh and report generation.
    """
    # Dynamic pathing based on date
    year_str = position_date.strftime("%Y")
    month_str = position_date.strftime("%m")
    target_folder = os.path.join(BASE_DIR, year_str, f"{year_str}-{month_str}")
    
    file_name = "Intercompany_Validation_Tool.xlsm"
    macro_name = "RefreshEverything"
    sheet_name = "Data_Check_Summary"

    # 1. Setup Directory
    if not os.path.exists(target_folder):
        os.makedirs(target_folder)

    source_template = os.path.join(TEMPLATE_DIR, file_name)
    destination_file = os.path.join(target_folder, file_name)

    # 2. Deploy Template
    shutil.copyfile(source_template, destination_file)

    if os.path.exists(destination_file):
        print(f"Processing: {destination_file}")
        xl_app = xw.App(visible=False)
        try:
            wb = xl_app.books.open(os.path.abspath(destination_file), update_links=False)
            ws = wb.sheets[sheet_name]
            
            # Update position date in the Excel tool
            ws.range('C3').value = position_date
            wb.app.calculate()

            # Execute the automation macro
            xl_app.api.Run(macro_name)
            tm.sleep(5) # Buffer for async calculations

            # Extract results from calculated cells
            invoice_error = "{:,.2f}".format(wb.sheets['PT_Check'].range('J1').value)
            pnl_mismatch = "{:,.2f}".format(wb.sheets['PnL_Check'].range('J1').value)

            wb.save()
            wb.close()
        finally:
            xl_app.quit()

        # 3. Archiving
        archive_name = f"Recon_Report_{position_date.strftime('%Y-%m-%d')}.xlsm"
        archive_path = os.path.join(BACKUP_DIR, archive_name)
        shutil.copyfile(destination_file, archive_path)

        # 4. Reporting Logic (Only sends if near month-end/specific threshold)
        if position_date.day >= 20:
            send_notification(position_date, invoice_error, pnl_mismatch, destination_file)
        else:
            print(f"Recon completed. Invoicing gap: {invoice_error}. PnL gap: {pnl_mismatch}. (Email suppressed).")

def send_notification(date_obj, inv_err, pnl_err, attachment_path):
    """Dispatches report via Outlook."""
    try:
        outlook = win32com.client.Dispatch('outlook.application')
        mail = outlook.CreateItem(0)
        mail.To = RECIPIENT_EMAIL
        mail.Subject = f'Inter-Entity Reconciliation Report - {date_obj.strftime("%d/%m/%Y")}'
        
        mail.Body = (
            f"Please find the reconciliation results for position date: {date_obj.strftime('%d/%m/%Y')}.\n\n"
            f"Invoicing Discrepancy: {inv_err}\n"
            f"PnL Mismatch: {pnl_err}\n\n"
            "Please review the attached file for detailed line-item breakdowns."
        )

        if os.path.isfile(attachment_path):
            mail.Attachments.Add(attachment_path)
            mail.Send()
            print("Notification email dispatched successfully.")
    except Exception as e:
        print(f"Failed to send email: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Finance ETL Pipeline")
    parser.add_argument("--date", type=str, help="Date in YYYY-MM-DD", default=None)
    args = parser.parse_args()

    holidays = get_bank_holidays()
    custom_bday = CustomBusinessDay(holidays=holidays)

    if args.date:
        target_date = datetime.strptime(args.date, '%Y-%m-%d').date()
    else:
        # Default to T-2 Business Days
        target_date = datetime.today().date() - (custom_bday * 2)

    run_reconciliation(target_date)
