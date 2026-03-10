# -*- coding: utf-8 -*-
"""
Multi-Account Bank Statement Parser (BNP Paribas Template)

Description:
This engine extracts transaction data and closing balances from unstructured 
PDF bank statements. It handles specific PDF encoding artifacts (duplicated chars) 
and standardizes data into a relational format for ERP ingestion.

Author: David Zadera (Portfolio Version)
"""

import os
import re
import argparse
import pandas as pd
import pdfplumber
from datetime import datetime

# --- CONFIGURATION ---
# In production, these should be set via environment variables or a config file
INBOUND_DIR = os.getenv("BANK_STMT_INBOUND", "data/inbound_statements/")
OUTBOUND_DIR = os.getenv("BANK_STMT_OUTBOUND", "data/processed_balances/")

def extract_text_from_pdf(pdf_path):
    """Extract raw text from all pages of a PDF."""
    text = ""
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text += page.extract_text() + "\n"
    return text

def parse_header_info(text):
    """Extracts metadata like Account Names, Numbers, and Closing Balances."""
    info = {}
    patterns = {
        'Account_Name': r'Account name:.*?((?:ENTITY_A|ENTITY_B)[^\n]*?)(?:\n|$)',
        'Bank_Name': r'Bank name:.*?BNP PARIBAS',
        'Account_Number': r'Account number:.*?([A-Z]{2}\d+)',
        'Date_Range': r'Date range:.*?(\d{2}/\d{2}/\d{4}\s*-\s*\d{2}/\d{2}/\d{4})',
        'Currency': r'Currency:\s*([A-Z]{3})',
        'Closing_Balance': r'Closing balance - \d+:\s*([\d,]+\.\d{2})'
    }

    for key, pattern in patterns.items():
        match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
        if match:
            info[key] = match.group(1).strip() if match.lastindex else match.group(0).strip()
    return info

def clean_duplicated_account_chars(account):
    """
    Fixes PDF encoding errors where characters appear duplicated 
    (e.g. 'FFRR7766...' instead of 'FR76...').
    """
    if len(str(account)) > 30: 
        cleaned = ''.join(account[i] for i in range(0, len(account), 2))
        if re.match(r'^[A-Z]{2}\d{10,30}$', cleaned):
            return cleaned
    return account

def parse_transactions(text):
    """Uses Regex to extract transaction rows from unstructured text blocks."""
    transactions = []
    # Pattern: [Book Date] [Value Date] [Type] [Description] [Amount]
    pattern = r'(\d{2}/\d{2}/\d{4}|)\s+(\d{2}/\d{2}/\d{4}|)\s*(TRF|CMZ|RTI|COM|)\s*([^\n]*?)\s*(-?\d{1,3}(?:,\d{3})*?\.\d{2}|-?\d+?\.\d{2}|)\s*(?:\n|$)'
    
    matches = re.findall(pattern, text, re.DOTALL | re.MULTILINE)

    for m in matches:
        transactions.append({
            'Book Date': m[0].strip(),
            'Value Date': m[1].strip(),
            'Type': m[2].strip(),
            'Description': m[3].strip(),
            'Amount': m[4].strip().replace(',', '')
        })
    return pd.DataFrame(transactions)

def process_statement(pdf_path, date_obj):
    """Orchestrates the extraction, cleaning, and export process."""
    if not os.path.exists(pdf_path):
        print(f"File not found: {pdf_path}")
        return

    text = extract_text_from_pdf(pdf_path)
    header = parse_header_info(text)
    df = parse_transactions(text)

    # Data Cleaning & Feature Engineering
    df['Amount'] = pd.to_numeric(df['Amount'], errors='coerce')
    df['Description'] = df['Description'].fillna("").str.strip()
    
    # Extract embedded account numbers within transaction descriptions
    df['Internal_Account'] = df['Description'].str.extract(r'number:\s*([A-Z0-9]+)', expand=False)
    df['Internal_Account'] = df['Internal_Account'].apply(clean_duplicated_account_chars)

    # Export Logic
    output_fn = f"Statement_Export_{date_obj.strftime('%Y%m%d')}.xlsx"
    output_path = os.path.join(OUTBOUND_DIR, output_fn)
    
    os.makedirs(OUTBOUND_DIR, exist_ok=True)
    
    with pd.ExcelWriter(output_path, engine='xlsxwriter') as writer:
        df.to_excel(writer, sheet_name='Transactions', index=False)
        # Summary logic here...
    
    print(f"Success: Processed data saved to {output_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Bank Statement PDF Scraper')
    parser.add_argument("--date", type=str, help="YYYY-MM-DD", default=None)
    args = parser.parse_args()

    target_date = pd.to_datetime(args.date) if args.date else pd.Timestamp.now() - pd.tseries.offsets.BDay(1)
    
    # Dynamic File Discovery
    date_path = target_date.strftime('%d%m%y')
    sample_pdf = os.path.join(INBOUND_DIR, date_path, f"BNP_{date_path}.pdf")
    
    process_statement(sample_pdf, target_date)
