#!/usr/bin/env python3
"""
Railway-specific script that only generates HTML reports
(Railway free tier blocks SMTP, so this version doesn't send emails)
"""
import sys
import os
from pathlib import Path

# Add email directory to path
sys.path.append(str(Path(__file__).parent / 'email'))

from create_html import get_user_positions, df_to_pretty_html_marketstyle
import pandas as pd

def main():
    print("=" * 60)
    print("Polymarket Report Generator for Railway")
    print("=" * 60)
    print("Note: Railway free tier blocks SMTP ports.")
    print("This script generates HTML reports only.")
    print("To send emails, upgrade to Railway paid tier or run locally.")
    print("=" * 60)

    # Default address (can be overridden by environment variable)
    address = os.getenv('POLYMARKET_ADDRESS', '0x22633134dc34f6c9a3bff51a0926c9d209714e26')

    # Allow command line override
    if len(sys.argv) > 1:
        address = sys.argv[1]

    print(f"\nGenerating report for address: {address}")

    try:
        # Get positions data
        df = get_user_positions(address)

        # Ensure df['title'] is present
        if 'title' not in df.columns and 'marketQuestion' in df.columns:
            df['title'] = df['marketQuestion']

        # Log filtering info
        original_count = len(df)
        if 'currentValue' in df.columns:
            df_temp = df.copy()
            df_temp['currentValue'] = pd.to_numeric(df_temp['currentValue'], errors="coerce")
            filtered_count = len(df_temp[df_temp['currentValue'] > 0])
            if filtered_count < original_count:
                print(f"Filtering: {original_count} positions → {filtered_count} positions (removed {original_count - filtered_count} with zero value)")

        # Generate HTML
        output_path = df_to_pretty_html_marketstyle(df, out_path="polymarket_positions.html")
        print(f"✅ HTML report saved to: {output_path}")

        # Provide instructions for accessing the report
        print("\n" + "=" * 60)
        print("Report Generated Successfully!")
        print("=" * 60)
        print("\nTo view the report:")
        print("1. Download the file: polymarket_positions.html")
        print("2. Open it in your web browser")
        print("\nTo send via email:")
        print("- Option 1: Upgrade to Railway paid tier (Team plan or higher)")
        print("- Option 2: Run the script locally with email flags")
        print("- Option 3: Use an email API service (SendGrid, Mailgun, etc.)")
        print("=" * 60)

    except Exception as e:
        print(f"\n❌ Error generating report: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()