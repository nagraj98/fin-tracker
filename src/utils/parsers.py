"""
Parser utilities for different transaction file formats
"""

import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime

def parse_chase_csv(file_path):
    """
    Parse Chase CSV transaction file
    
    Args:
        file_path (Path): Path to the Chase CSV file
    
    Returns:
        pd.DataFrame: Standardized DataFrame with transaction data
    """
    try:
        # Read the CSV file
        df = pd.read_csv(file_path, encoding='utf-8')
        
        # Common column names in Chase statements
        # Expected columns: Transaction Date,Post Date,Description,Category,Type,Amount,Memo
        
        # Standardize column names
        column_mapping = {
            'Transaction Date': 'Date',
            'Post Date': 'PostDate',
            'Description': 'Description',
            'Category': 'Category',
            'Type': 'TransactionType',
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
        # Read the CSV file
        df = pd.read_csv(file_path, encoding='utf-8')
        
        # Common column names in Discover statements
        # Expected columns: Trans. Date,Post Date,Description,Amount,Category
        
        # Standardize column names
        column_mapping = {
            'Trans. Date': 'Date',
            'Transaction Date': 'Date',
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
