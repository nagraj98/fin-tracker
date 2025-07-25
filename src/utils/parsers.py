"""
Parser utilities for different transaction file formats
"""

import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime

def parse_chase_csv(file_path):
    """
    Parse Chase CSV transaction file. Handles both credit card and checking/debit account formats.
    
    Args:
        file_path (Path): Path to the Chase CSV file
    
    Returns:
        pd.DataFrame: Standardized DataFrame with transaction data
    """
    try:
        # Read the CSV file
        df = pd.read_csv(file_path, encoding='utf-8', index_col=False)
        
        # Determine which format the file is based on columns
        if 'Details' in df.columns and 'Posting Date' in df.columns and 'Balance' in df.columns:
            # This is a checking/debit account format
            # Expected columns: Details, Posting Date, Description, Amount, Type, Balance, Check or Slip #
            print(f"Detected Chase checking/debit account format for {file_path}")
            column_mapping = {
                'Posting Date': 'Date',  # Use Posting Date as the transaction date
                'Posting Date': 'PostDate',
                'Details': 'CredDeb',  # Details column contains credit/debit information
                'Description': 'Description',
                'Amount': 'Amount',
                'Type': 'TransactionType',
                # 'Balance': 'Balance', this can be included if needed
                'Check or Slip #': 'CheckNumber'
            }
        else:
            # This is a credit card format
            # Expected columns: Transaction Date, Post Date, Description, Category, Type, Amount, Memo
            print(f"Detected Chase credit card format for {file_path}")
            column_mapping = {
                'Transaction Date': 'Date',
                'Post Date': 'PostDate',
                'Description': 'Description',
                'Category': 'Category',
                'Type': 'TransactionType',
                'Amount': 'Amount',
                'Memo': 'Memo'
            }
        
        # Only keep columns that exist in the file
        existing_columns = set(df.columns).intersection(column_mapping.keys())
        if not existing_columns:
            print(f"Warning: No recognized columns found in {file_path}")
            print(f"Available columns: {', '.join(df.columns)}")
            return None
            
        df = df[[col for col in df.columns if col in existing_columns]]
        
        # Rename columns
        df = df.rename(columns={col: column_mapping[col] for col in existing_columns})

        print(df.head(2))
        
        # Convert date columns to datetime
        if 'Date' in df.columns:
            df['Date'] = pd.to_datetime(df['Date']).dt.date
        
        if 'PostDate' in df.columns:
            df['PostDate'] = pd.to_datetime(df['PostDate']).dt.date
        
        # Ensure amount is properly signed (negative for expenses, positive for income)
        if 'Amount' in df.columns:
            df['Amount'] = df['Amount'].astype(float)
        
        return df
    
    except Exception as e:
        print(f"Error parsing Chase CSV {file_path}: {str(e)}")
        return None

def parse_discover_csv(file_path):
    """
    Parse Discover CSV transaction file
    
    Args:
        file_path (Path): Path to the Discover CSV file
    
    Returns:
        pd.DataFrame: Standardized DataFrame with transaction data
    """
    try:
        df = pd.read_csv(file_path, encoding='utf-8')
        
        # Standardize column names
        column_mapping = {
            'Trans. Date': 'Date',
            # 'Transaction Date': 'Date',
            'Post Date': 'PostDate',
            'Description': 'Description',
            'Category': 'Category',
            'Amount': 'Amount'
        }
        
        # Only keep columns that exist in the file
        existing_columns = set(df.columns).intersection(column_mapping.keys())
        df = df[[col for col in column_mapping.keys() if col in existing_columns]]
        
        # Rename columns
        df = df.rename(columns={col: column_mapping[col] for col in existing_columns})
        
        # Convert date columns to datetime
        if 'Date' in df.columns:
            df['Date'] = pd.to_datetime(df['Date']).dt.date
        
        if 'PostDate' in df.columns:
            df['PostDate'] = pd.to_datetime(df['PostDate']).dt.date
        
        # Discover typically reports expenses as positive numbers, so we need to flip the sign
        if 'Amount' in df.columns:
            df['Amount'] = -1 * df['Amount'].astype(float)
        
        # Add TransactionType column if it doesn't exist
        if 'TransactionType' not in df.columns:
            df['TransactionType'] = np.where(df['Amount'] >= 0, 'CREDIT', 'DEBIT')
        
        return df
    
    except Exception as e:
        print(f"Error parsing Discover CSV {file_path}: {str(e)}")
        return None
