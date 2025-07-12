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

# Load environment variables
load_dotenv()

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
    
    # Look for Chase files
    chase_files = list(month_dir.glob("*Chase*.CSV"))
    if chase_files:
        transaction_files["chase"] = chase_files
    
    # Look for Discover files
    discover_files = list(month_dir.glob("*discover*.csv"))
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
            account_name = file_path.stem.split('_')[0][-4:] if '_' in file_path.stem else "0000"
            account_id = f"chase{account_name}" if account_name.isdigit() else account_name
            
            df = parse_chase_csv(file_path)
            if df is not None and not df.empty:
                df["Account"] = account_id
                all_transactions.append(df)
    
    # Process Discover files
    if "discover" in transaction_files:
        for file_path in transaction_files["discover"]:
            account_name = file_path.stem.split('_')[-1] if '_' in file_path.stem else "discover"
            account_id = f"discover{account_name}" if account_name.isdigit() else account_name
            
            df = parse_discover_csv(file_path)
            if df is not None and not df.empty:
                df["Account"] = account_id
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
