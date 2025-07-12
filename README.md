# Personal Finance Tracker

A Python-based tool for consolidating and analyzing personal finance data from multiple sources.

## Overview

This tool helps you combine transaction data from different financial institutions (currently supporting Chase and Discover) into a single consolidated format for analysis and tracking.

## Features

- Automatically detects and processes transaction files from OneDrive
- Supports Chase and Discover transaction formats
- Adds account identification to each transaction
- Combines all transactions into a single CSV file or DataFrame
- Provides transaction summaries

## Setup

1. Clone this repository
2. Install the dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Copy `.env.example` to `.env` and update with your OneDrive path:
   ```
   cp .env.example .env
   # Edit .env with your favorite editor
   ```

## Usage

### Basic Usage

Combine the current month's transactions:

```bash
python src/combine_transactions.py
```

### Specify Month

Combine transactions from a specific month:

```bash
python src/combine_transactions.py --month "Jun 2025"
```

### Custom Output File

```bash
python src/combine_transactions.py --output "my_transactions.csv"
```

## File Structure

The script expects your files to be organized in OneDrive as follows:

```
OneDrive/
  FinTracker/
    Data/
      Jun 2025/
        discover_1234.csv
        chase_1182.csv
      Jul 2025/
        discover_1234.csv
        chase_1182.csv
```

## Extending

To add support for other financial institutions:

1. Create a new parser in `src/utils/parsers.py`
2. Add detection and processing logic in `combine_transactions.py`
