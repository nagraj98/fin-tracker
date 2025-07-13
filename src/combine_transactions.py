#!/usr/bin/env python3
"""
Finance Tracker - Transaction Combiner

This script combines transaction data from different financial institutions (Chase, Discover)
into a single CSV file or DataFrame.
"""

import os
import pandas as pd
import argparse
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

from utils.parsers import parse_chase_csv, parse_discover_csv
import csv

# Load environment variables
load_dotenv()

def identify_file_type(file_path):
    """
    Identify the type of CSV file based on its headers
    
    Args:
        file_path (Path): Path to the CSV file
    
    Returns:
        tuple: (bank_name, account_type)
    """
    try:
        # Read just the header row to identify the file
        with open(file_path, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            headers = next(reader, [])
            
        headers_str = ','.join(headers).lower()
        
        # Identify bank
        bank_name = None
        if 'chase' in file_path.stem.lower():
            bank_name = 'chase'
        elif 'discover' in file_path.stem.lower():
            bank_name = 'discover'
            
        # Identify account type
        account_type = None
        if bank_name == 'chase':
            if 'details' in headers_str and 'balance' in headers_str:
                account_type = 'checking'
            elif 'transaction date' in headers_str and 'category' in headers_str:
                account_type = 'credit'
                
        elif bank_name == 'discover':
            account_type = 'credit'  # Discover is primarily credit cards
            
        return bank_name, account_type
    
    except Exception as e:
        print(f"Error identifying file type for {file_path}: {str(e)}")
        return None, None

def get_onedrive_path():
    """Get the OneDrive path from environment variable or user input"""
    onedrive_path = os.getenv("ONEDRIVE_PATH")
    if not onedrive_path:
        print("OneDrive path not found in environment variables.")
        onedrive_path = input("Please enter your OneDrive path: ")
    return Path(onedrive_path)

def find_transaction_files(base_dir, month_year=None):
    """
    Find transaction files in the given directory structure
    
    Args:
        base_dir (Path): Base directory to search in
        month_year (str, optional): Month and year in format 'MMM YYYY'. Defaults to None.
    
    Returns:
        dict: Dictionary with keys as account types and values as lists of file paths
    """
    fintracker_dir = base_dir / "FinTracker" / "Data"
    
    if not fintracker_dir.exists():
        raise FileNotFoundError(f"Directory not found: {fintracker_dir}")
    
    # If month_year is not provided, use the current month
    if month_year is None:
        month_year = datetime.now().strftime("%b %Y")
    
    month_dir = fintracker_dir / month_year
    
    if not month_dir.exists():
        raise FileNotFoundError(f"Directory for {month_year} not found: {month_dir}")
    
    # Find all CSV files
    transaction_files = {}
    
    # Look for Chase files - be case-insensitive with both CSV and csv extensions
    chase_files = list(month_dir.glob("*[Cc][Hh][Aa][Ss][Ee]*.[Cc][Ss][Vv]"))
    if chase_files:
        transaction_files["chase"] = chase_files
    
    # Look for Discover files - be case-insensitive with both CSV and csv extensions
    discover_files = list(month_dir.glob("*[Dd][Ii][Ss][Cc][Oo][Vv][Ee][Rr]*.[Cc][Ss][Vv]"))
    if discover_files:
        transaction_files["discover"] = discover_files
    
    return transaction_files

def process_transaction_files(transaction_files):
    """
    Process transaction files and combine them into a single DataFrame
    
    Args:
        transaction_files (dict): Dictionary with keys as account types and values as lists of file paths
    
    Returns:
        pd.DataFrame: Combined DataFrame of all transactions
    """
    all_transactions = []
    
    # Process Chase files
    if "chase" in transaction_files:
        for file_path in transaction_files["chase"]:
            # Try to extract account number from filename
            filename = file_path.stem
            
            # Identify file type based on content
            bank_name, detected_account_type = identify_file_type(file_path)
            
            # Extract account numbers using different patterns
            account_number = None
            
            # Look for patterns like "Chase_1234" or "Chase1234"
            if '_' in filename:
                parts = filename.split('_')
                for part in parts:
                    if part.isdigit() and len(part) == 4:
                        account_number = part
                        break
                    # Handle case where number might be at the end of a part
                    digits = ''.join(filter(str.isdigit, part))
                    if digits and len(digits) >= 4:
                        account_number = digits[-4:]
                        break
            else:
                # Try to extract last 4 digits from the filename
                digits = ''.join(filter(str.isdigit, filename))
                if digits and len(digits) >= 4:
                    account_number = digits[-4:]
            
            # If no account type was detected from file content, try to infer from filename
            if not detected_account_type:
                if "check" in filename.lower() or "debit" in filename.lower():
                    detected_account_type = "checking"
                elif "credit" in filename.lower() or "card" in filename.lower():
                    detected_account_type = "credit"
            
            # Create account ID
            if account_number:
                if detected_account_type:
                    account_id = f"chase_{detected_account_type}{account_number}"
                else:
                    account_id = f"chase{account_number}"
            else:
                if detected_account_type:
                    account_id = f"chase_{detected_account_type}"
                else:
                    account_id = "chase_unknown"
            
            print(f"Processing Chase file: {file_path.name} (Account ID: {account_id}, Type: {detected_account_type})")
            
            df = parse_chase_csv(file_path)
            if df is not None and not df.empty:
                df["Account"] = account_id
                
                # Add account type if it was detected
                if detected_account_type:
                    df["AccountType"] = detected_account_type
                
                all_transactions.append(df)
    
    # Process Discover files
    if "discover" in transaction_files:
        for file_path in transaction_files["discover"]:
            # Try to extract account number from filename
            filename = file_path.stem
            
            # Identify file type based on content
            bank_name, detected_account_type = identify_file_type(file_path)
            
            # Extract account numbers using different patterns
            account_number = None
            
            # Look for patterns like "Discover_1234" or "Discover1234"
            if '_' in filename:
                parts = filename.split('_')
                for part in parts:
                    if part.isdigit() and len(part) == 4:
                        account_number = part
                        break
                    # Handle case where number might be at the end of a part
                    digits = ''.join(filter(str.isdigit, part))
                    if digits and len(digits) >= 4:
                        account_number = digits[-4:]
                        break
            else:
                # Try to extract last 4 digits from the filename
                digits = ''.join(filter(str.isdigit, filename))
                if digits and len(digits) >= 4:
                    account_number = digits[-4:]
            
            # Create account ID
            if account_number:
                account_id = f"discover{account_number}"
            else:
                account_id = "discover"
            
            print(f"Processing Discover file: {file_path.name} (Account ID: {account_id})")
            
            df = parse_discover_csv(file_path)
            if df is not None and not df.empty:
                df["Account"] = account_id
                
                # Add account type (usually credit for Discover)
                df["AccountType"] = "credit"
                
                all_transactions.append(df)
    
    # Combine all transactions
    if all_transactions:
        return pd.concat(all_transactions, ignore_index=True)
    else:
        return pd.DataFrame()

def main():
    parser = argparse.ArgumentParser(description="Combine financial transaction data from multiple sources")
    parser.add_argument("--month", type=str, help="Month and year in format 'MMM YYYY' (e.g., 'Jun 2025')")
    parser.add_argument("--output", type=str, default="combined_transactions.csv", 
                        help="Output file name (default: combined_transactions.csv)")
    
    args = parser.parse_args()
    
    try:
        onedrive_path = get_onedrive_path()
        
        print(f"Searching for transaction files for {args.month or 'current month'}...")
        transaction_files = find_transaction_files(onedrive_path, args.month)
        
        if not transaction_files:
            print("No transaction files found.")
            return
        
        print(f"Found transaction files: {transaction_files}")
        
        # Process the transaction files
        combined_df = process_transaction_files(transaction_files)
        
        if combined_df.empty:
            print("No transactions were processed.")
            return
        
        # Sort by date
        if "Date" in combined_df.columns:
            combined_df = combined_df.sort_values("Date")
        
        # Save to CSV
        output_path = Path(args.output)
        combined_df.to_csv(output_path, index=False)
        print(f"Combined transactions saved to {output_path}")
        
        # Display summary
        print("\nTransaction Summary:")
        print(f"Total transactions: {len(combined_df)}")
        print(f"Date range: {combined_df['Date'].min()} to {combined_df['Date'].max()}")
        print("\nTransactions by account:")
        print(combined_df["Account"].value_counts())
        
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    main()
