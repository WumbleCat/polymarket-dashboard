import pandas as pd
import requests

def get_user_positions(address: str):
    URL = f"https://data-api.polymarket.com/positions?user={address}"

    data = requests.get(URL).json()

    df = pd.DataFrame(data)
    return df

import pandas as pd
import numpy as np
from pathlib import Path

def df_to_pretty_html_marketstyle(
    df: pd.DataFrame,
    out_path: str = "polymarket_positions.html",
    title_col: str = "title",          # title text
    slug_col: str = "marketSlug",      # for hyperlink
    logo_col: str = "icon",            # Polymarket logo/icon column
    side_col: str = "outcome",         # "Yes"/"No"/"Up"/"Down"
    size_col: str = "size",            # shares
    avg_price_col: str = "avgPrice",   # $ (0.63) or ¢ (63)
    cur_price_col: str = "curPrice",   # same
    value_col: str = "currentValue",   # $
    cash_pnl_col: str = "cashPnl",     # $
    pct_pnl_col: str = "percentPnl",   # 0–1 or 0–100
):
    """
    Render a Polymarket-like HTML table:
      MARKET (logo + clickable title + subline), AVG (¢), CURRENT (¢), VALUE ($ + PnL)
    Automatically sorts by value_col in descending order.
    """
    df = df.copy()

    # ---- helpers ----
    def _to_pct01(colname):
        if colname not in df.columns:
            return pd.Series([np.nan] * len(df))
        col = pd.to_numeric(df[colname], errors="coerce")
        if col.notna().any():
            s = col.dropna().iloc[0]
            if abs(s) > 1.5:
                col = col / 100.0
        return col

    def _to_cents(colname):
        if colname not in df.columns:
            return pd.Series([np.nan]*len(df))
        col = pd.to_numeric(df[colname], errors="coerce")
        med = col.dropna().median() if col.notna().any() else np.nan
        if pd.notna(med) and med <= 1.5:
            col = col * 100.0
        return col

    def _fmt_cents(x):
        if pd.isna(x): return ""
        return f"{float(x):.0f}¢"

    def _fmt_money(x):
        if pd.isna(x): return ""
        return f"${float(x):,.2f}"

    def _fmt_pnl_line(cash, pct01):
        if pd.isna(cash) and pd.isna(pct01):
            return ""
        cash_s = _fmt_money(cash) if pd.notna(cash) else ""
        pct_s = f"{(pct01*100):.2f}%" if pd.notna(pct01) else ""
        sign = "pos" if (pd.notna(cash) and cash >= 0) or (pd.isna(cash) and pd.notna(pct01) and pct01 >= 0) else "neg"
        inner = []
        if cash_s: inner.append(cash_s)
        if pct_s: inner.append(f"({pct_s})")
        return f'<span class="pnl {sign}">{" ".join(inner)}</span>'

    # ---- sort by value and filter out zero values ----
    if value_col in df.columns:
        df[value_col] = pd.to_numeric(df[value_col], errors="coerce")
        # Filter out positions with zero or null value
        df = df[df[value_col] > 0].copy()
        df = df.sort_values(by=value_col, ascending=False).reset_index(drop=True)

    # ---- MARKET cell ----
    titles = (
        df[title_col].astype(str)
        if title_col in df.columns
        else (df["marketQuestion"].astype(str) if "marketQuestion" in df.columns else pd.Series([""]*len(df)))
    )
    slugs = df[slug_col].astype(str) if slug_col in df.columns else pd.Series([None]*len(df))
    logos = df[logo_col].astype(str) if logo_col in df.columns else pd.Series([""]*len(df))
    side = df[side_col].astype(str) if side_col in df.columns else pd.Series([""]*len(df))
    shares = pd.to_numeric(df[size_col], errors="coerce") if size_col in df.columns else pd.Series([np.nan]*len(df))
    avg_c = _to_cents(avg_price_col)

    market_cells = []
    for i in range(len(df)):
        title_txt = titles.iloc[i] if pd.notna(titles.iloc[i]) else ""
        slug = slugs.iloc[i] if pd.notna(slugs.iloc[i]) and str(slugs.iloc[i]).lower() != "nan" else None
        logo = logos.iloc[i] if pd.notna(logos.iloc[i]) and str(logos.iloc[i]).strip() != "" else ""
        side_val = side.iloc[i] if pd.notna(side.iloc[i]) and side.iloc[i] != "" else ""

        # link & logo
        if slug:
            link = f'https://polymarket.com/market/{slug}'
            title_html = f'<a class="title-link" target="_blank" href="{link}">{title_txt}</a>'
        else:
            title_html = f'<span class="title-text">{title_txt}</span>'
        logo_html = f'<img class="logo" src="{logo}" alt="logo">' if logo else ""

        # Create chip with appropriate color
        if side_val.lower() == "yes":
            chip_html = f'<span class="chip chip-yes">{side_val}</span>'
        elif side_val.lower() == "no":
            chip_html = f'<span class="chip chip-no">{side_val}</span>'
        elif side_val != "":
            chip_html = f'<span class="chip">{side_val}</span>'
        else:
            chip_html = ''

        # Position info
        position_bits = []
        if pd.notna(shares.iloc[i]):
            position_bits.append(f'{shares.iloc[i]:,.1f} shares')
        if pd.notna(avg_c.iloc[i]):
            position_bits.append(f'at {_fmt_cents(avg_c.iloc[i])}')
        position_info = " ".join(position_bits)
        position_html = f'<div class="position-info">{position_info}</div>' if position_info else ""

        # New layout with fixed chip position
        market_cells.append(
            f'''<div class="market-wrap">
                {logo_html}
                <div class="market-content">
                    <div class="market-header">
                        <div class="market-title">{title_html}</div>
                        <div class="market-chip">{chip_html}</div>
                    </div>
                    {position_html}
                </div>
            </div>'''
        )

    # ---- AVG / CURRENT / VALUE ----
    cur_c = _to_cents(cur_price_col)
    avg_disp = [_fmt_cents(x) for x in avg_c]
    cur_disp = [_fmt_cents(x) for x in cur_c]

    value = pd.to_numeric(df[value_col], errors="coerce") if value_col in df.columns else pd.Series([np.nan]*len(df))
    cash = pd.to_numeric(df[cash_pnl_col], errors="coerce") if cash_pnl_col in df.columns else pd.Series([np.nan]*len(df))
    pct01 = _to_pct01(pct_pnl_col)

    value_cells = []
    for i in range(len(df)):
        vline = _fmt_money(value.iloc[i]) if pd.notna(value.iloc[i]) else ""
        pline = _fmt_pnl_line(
            cash.iloc[i] if i < len(cash) else np.nan,
            pct01.iloc[i] if i < len(pct01) else np.nan
        )
        value_cells.append(f'<div class="val">{vline}</div>' + (f'<div class="sub">{pline}</div>' if pline else ""))

    display = pd.DataFrame({
        "MARKET": market_cells,
        "AVG": avg_disp,
        "CURRENT": cur_disp,
        "VALUE": value_cells,
    })

    # ---- Build HTML table with separators every 5 rows ----
    rows_html = []
    for i, row in display.iterrows():
        # Add separator every 5 rows (but not before first row)
        if i > 0 and i % 5 == 0:
            rows_html.append('<tr class="separator-row"><td colspan="4"></td></tr>')

        # Add data row
        row_html = '<tr>'
        for col in display.columns:
            row_html += f'<td>{row[col]}</td>'
        row_html += '</tr>'
        rows_html.append(row_html)

    tbody_content = '\n'.join(rows_html)

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Polymarket Positions Report</title>
    <!--[if mso]>
    <noscript>
        <xml>
            <o:OfficeDocumentSettings>
                <o:PixelsPerInch>96</o:PixelsPerInch>
            </o:OfficeDocumentSettings>
        </xml>
    </noscript>
    <![endif]-->
    <style>
        /* Reset styles for email clients */
        body, table, td, a {{ -webkit-text-size-adjust: 100%; -ms-text-size-adjust: 100%; }}
        table, td {{ mso-table-lspace: 0pt; mso-table-rspace: 0pt; }}
        img {{ -ms-interpolation-mode: bicubic; border: 0; outline: none; text-decoration: none; }}

        /* Email body styles */
        body {{
            margin: 0 !important;
            padding: 0 !important;
            background-color: #f4f7fa !important;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, Arial, sans-serif !important;
        }}

        /* Container */
        .email-container {{
            max-width: 680px;
            margin: 0 auto;
            background-color: #ffffff;
        }}

        /* Header styles */
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 30px 20px;
            text-align: center;
        }}

        .header h1 {{
            margin: 0;
            color: #ffffff;
            font-size: 28px;
            font-weight: 600;
            text-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}

        /* Stats bar */
        .stats-bar {{
            background-color: #f8fafc;
            padding: 20px;
            border-bottom: 2px solid #e2e8f0;
        }}

        .stats-container {{
            display: table;
            width: 100%;
            table-layout: fixed;
        }}

        .stat-item {{
            display: table-cell;
            text-align: center;
            padding: 0 10px;
        }}

        .stat-value {{
            font-size: 24px;
            font-weight: bold;
            color: #4a5568;
        }}

        .stat-label {{
            font-size: 12px;
            color: #718096;
            margin-top: 4px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}

        /* Table styles */
        .positions-table {{
            width: 100%;
            border-collapse: separate;
            border-spacing: 0;
            margin: 0;
            padding: 20px;
            background-color: #ffffff;
        }}

        .positions-table th {{
            background: linear-gradient(135deg, #f6f9fc 0%, #e9ecef 100%);
            color: #2d3748;
            font-weight: 600;
            font-size: 12px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            padding: 12px 15px;
            text-align: left;
            border-bottom: 2px solid #cbd5e0;
        }}

        .positions-table td {{
            padding: 15px;
            border-bottom: 1px solid #e2e8f0;
            color: #4a5568;
            font-size: 14px;
            vertical-align: middle;
            background-color: #ffffff;
        }}

        /* Alternating row colors */
        .positions-table tr:nth-child(odd) td {{
            background-color: #fafbfc;
        }}

        /* Hover effect for desktop */
        .positions-table tr:hover td {{
            background-color: #f0f4f8 !important;
            transition: background-color 0.2s ease;
        }}

        /* Separator row styling */
        .separator-row td {{
            padding: 0 !important;
            height: 3px !important;
            background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
            border: none !important;
        }}

        /* Market cell styling */
        .market-wrap {{
            display: flex;
            align-items: flex-start;
            width: 100%;
        }}

        .logo {{
            width: 32px;
            height: 32px;
            border-radius: 8px;
            margin-right: 12px;
            flex-shrink: 0;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}

        .market-content {{
            flex: 1;
            min-width: 0;
        }}

        .market-header {{
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            gap: 10px;
            margin-bottom: 4px;
        }}

        .market-title {{
            flex: 1;
            min-width: 0;
        }}

        .market-chip {{
            flex-shrink: 0;
        }}

        .title-link {{
            color: #5b21b6;
            text-decoration: none;
            font-weight: 500;
            font-size: 14px;
            display: block;
        }}

        .title-link:hover {{
            color: #7c3aed;
            text-decoration: underline;
        }}

        .title-text {{
            color: #2d3748;
            font-weight: 500;
            font-size: 14px;
            display: block;
        }}

        /* Position info styling */
        .position-info {{
            color: #718096;
            font-size: 12px;
            margin-top: 2px;
        }}

        /* Chip styling */
        .chip {{
            display: inline-block;
            padding: 4px 12px;
            border-radius: 12px;
            font-size: 11px;
            font-weight: 700;
            color: #ffffff;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            white-space: nowrap;
        }}

        .chip-yes {{
            background: linear-gradient(135deg, #10b981 0%, #059669 100%);
        }}

        .chip-no {{
            background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
        }}

        .chip:not(.chip-yes):not(.chip-no) {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        }}

        /* Value styling */
        .val {{
            font-weight: 600;
            font-size: 15px;
            color: #2d3748;
        }}

        /* PnL styling */
        .pnl {{
            font-weight: 500;
            font-size: 13px;
        }}

        .pnl.pos {{
            color: #10b981;
        }}

        .pnl.neg {{
            color: #ef4444;
        }}

        /* Price columns */
        .positions-table td:nth-child(2),
        .positions-table td:nth-child(3) {{
            font-weight: 500;
            color: #4a5568;
            text-align: center;
        }}

        /* Footer */
        .footer {{
            background-color: #f8fafc;
            padding: 30px 20px;
            text-align: center;
            border-top: 2px solid #e2e8f0;
        }}

        .footer-text {{
            color: #718096;
            font-size: 12px;
            margin: 0;
        }}

        .footer-link {{
            color: #667eea;
            text-decoration: none;
        }}

        /* Mobile responsiveness */
        @media only screen and (max-width: 600px) {{
            .email-container {{
                width: 100% !important;
            }}

            .header h1 {{
                font-size: 24px;
            }}

            .positions-table {{
                padding: 10px;
            }}

            .positions-table th,
            .positions-table td {{
                padding: 10px 8px;
                font-size: 12px;
            }}

            .logo {{
                width: 24px;
                height: 24px;
            }}

            .stat-value {{
                font-size: 20px;
            }}
        }}
    </style>
</head>
<body>
    <div class="email-container">
        <!-- Header -->
        <div class="header">
            <h1>📊 Polymarket Positions Report</h1>
        </div>

        <!-- Stats Bar -->
        <div class="stats-bar">
            <div class="stats-container">
                <div class="stat-item">
                    <div class="stat-value">{len(df)}</div>
                    <div class="stat-label">Total Positions</div>
                </div>
                <div class="stat-item">
                    <div class="stat-value">${value.sum():,.0f}</div>
                    <div class="stat-label">Total Value</div>
                </div>
                <div class="stat-item">
                    <div class="stat-value" style="color: {'#10b981' if cash.sum() >= 0 else '#ef4444'}">
                        ${cash.sum():+,.0f}
                    </div>
                    <div class="stat-label">Total P&L</div>
                </div>
            </div>
        </div>

        <!-- Positions Table -->
        <table class="positions-table">
            <thead>
                <tr>
                    <th>MARKET</th>
                    <th style="text-align: center;">AVG</th>
                    <th style="text-align: center;">CURRENT</th>
                    <th>VALUE</th>
                </tr>
            </thead>
            <tbody>
                {tbody_content}
            </tbody>
        </table>

        <!-- Footer -->
        <div class="footer">
            <p class="footer-text">
                Generated on {pd.Timestamp.now().strftime('%B %d, %Y at %I:%M %p')}
            </p>
            <p class="footer-text">
                View on <a href="https://polymarket.com" class="footer-link">Polymarket.com</a>
            </p>
        </div>
    </div>
</body>
</html>"""

    Path(out_path).write_text(html, encoding="utf-8")
    return out_path



def create_and_send_report(
    address: str,
    recipient_email: str = None,
    send_email: bool = False,
    html_path: str = "polymarket_positions.html"
):
    """
    Create HTML report and optionally send via email
    Note: Positions with zero value are automatically filtered out

    Args:
        address: Polymarket wallet address
        recipient_email: Email to send report to
        send_email: Whether to send email after creating HTML
        html_path: Path to save HTML file
    """
    # Get positions data
    df = get_user_positions(address)

    # Ensure df['title'] is present; if your API returns 'marketQuestion', you can map:
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

    # Generate HTML (filtering happens inside this function)
    out = df_to_pretty_html_marketstyle(df, out_path=html_path)
    print("Saved HTML to:", out)

    # Optionally send email
    if send_email and recipient_email:
        try:
            from gmail_sender import GmailSender

            sender = GmailSender()

            # Read the HTML content
            with open(html_path, 'r', encoding='utf-8') as f:
                html_content = f.read()

            # Send email
            success = sender.send_email(
                to_emails=recipient_email,
                subject=f"Polymarket Positions Report - {address[:8]}...",
                body_html=html_content,
                body_text="Please view this email in HTML format for the best experience."
            )

            if success:
                print(f"Email sent successfully to {recipient_email}")
            else:
                print("Failed to send email")

            return out, success
        except ValueError as e:
            if "GMAIL_EMAIL" in str(e) or "GMAIL_APP_PASSWORD" in str(e):
                print(f"\n⚠️ Email configuration error: {str(e)}")
                print("HTML report was generated but email was not sent.")
                print("To enable email sending, configure environment variables in Railway.")
                return out, False
            else:
                raise

    return out, None


if __name__ == "__main__":
    import sys
    import os
    from pathlib import Path
    from dotenv import load_dotenv

    # Try multiple methods to load environment variables
    # Method 1: Load from .env file in parent directory
    env_path = Path(__file__).parent.parent / '.env'
    if env_path.exists():
        load_dotenv(env_path)
        print(f"Loaded .env from {env_path}")

    # Method 2: Load from .env in current directory
    load_dotenv()

    # Method 3: Check if running in Railway (Railway sets this)
    if os.getenv('RAILWAY_ENVIRONMENT'):
        print("Running in Railway environment")

    # Debug: Print environment variable status (without showing sensitive values)
    print(f"GMAIL_EMAIL configured: {'Yes' if os.getenv('GMAIL_EMAIL') else 'No'}")
    print(f"GMAIL_APP_PASSWORD configured: {'Yes' if os.getenv('GMAIL_APP_PASSWORD') else 'No'}")

    # Default address
    address = "0x22633134dc34f6c9a3bff51a0926c9d209714e26"

    # Check command line arguments
    if len(sys.argv) > 1 and not sys.argv[1].startswith("-"):
        address = sys.argv[1]

    # Check if email sending is requested
    # In Railway, default to NOT sending email unless explicitly requested
    if os.getenv('RAILWAY_ENVIRONMENT'):
        # In Railway, only send email if explicitly requested with --send-email flag
        send_email = "--send-email" in sys.argv or "-e" in sys.argv
        if not send_email:
            print("Running in Railway: Generating HTML report only (no email)")
            print("To send email, use: python email/create_html.py --send-email recipient@example.com")
    else:
        # Local environment - check for email flag
        send_email = "--send-email" in sys.argv or "-e" in sys.argv

    recipient = None

    if send_email:
        # Look for email after --send-email or -e flag
        for i, arg in enumerate(sys.argv):
            if arg in ["--send-email", "-e"] and i + 1 < len(sys.argv):
                recipient = sys.argv[i + 1]
                break

        if not recipient or recipient.startswith("-"):
            print("Please provide recipient email: python create_html.py [address] --send-email recipient@example.com")
            sys.exit(1)

    # Create and optionally send report
    try:
        out, email_sent = create_and_send_report(
            address=address,
            recipient_email=recipient,
            send_email=send_email
        )

        if email_sent is False:
            print("\nFailed to send email. Check configuration:")
            print("1. Ensure GMAIL_EMAIL is set in Railway environment variables")
            print("2. Ensure GMAIL_APP_PASSWORD is set in Railway environment variables")
            print("3. Check Railway logs for more details")
    except Exception as e:
        print(f"Error: {str(e)}")
        if "GMAIL_EMAIL" in str(e) or "GMAIL_APP_PASSWORD" in str(e):
            print("\n📧 Email Configuration Required:")
            print("Please set the following in Railway Service Variables:")
            print("  GMAIL_EMAIL=your-email@gmail.com")
            print("  GMAIL_APP_PASSWORD=your-16-char-app-password")
            print("\nTo set these:")
            print("1. Go to your Railway service")
            print("2. Click on 'Variables' tab")
            print("3. Add the variables above")
            print("4. Redeploy the service")