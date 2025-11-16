"""
Example script for sending emails with Gmail SMTP
Demonstrates various email sending scenarios
"""
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from gmail_sender import GmailSender
from smtp_config import SMTPConfig


def example_basic_email():
    """Send a basic text email"""
    sender = GmailSender()

    success = sender.send_email(
        to_emails="recipient@example.com",
        subject="Test Email from Polymarket Analysis",
        body_text="This is a test email sent from the Polymarket Analysis application."
    )

    return success


def example_html_email():
    """Send an HTML formatted email"""
    sender = GmailSender()

    html_content = """
    <html>
        <body style="font-family: Arial, sans-serif; padding: 20px;">
            <h2 style="color: #333;">Polymarket Analysis Report</h2>
            <p>This is an HTML email with formatted content.</p>

            <table style="border-collapse: collapse; width: 100%; margin-top: 20px;">
                <tr style="background-color: #f2f2f2;">
                    <th style="border: 1px solid #ddd; padding: 8px;">Market</th>
                    <th style="border: 1px solid #ddd; padding: 8px;">Probability</th>
                    <th style="border: 1px solid #ddd; padding: 8px;">Volume</th>
                </tr>
                <tr>
                    <td style="border: 1px solid #ddd; padding: 8px;">Sample Market 1</td>
                    <td style="border: 1px solid #ddd; padding: 8px;">75%</td>
                    <td style="border: 1px solid #ddd; padding: 8px;">$100,000</td>
                </tr>
                <tr>
                    <td style="border: 1px solid #ddd; padding: 8px;">Sample Market 2</td>
                    <td style="border: 1px solid #ddd; padding: 8px;">60%</td>
                    <td style="border: 1px solid #ddd; padding: 8px;">$50,000</td>
                </tr>
            </table>

            <p style="margin-top: 20px; color: #666; font-size: 12px;">
                This email was generated automatically by the Polymarket Analysis system.
            </p>
        </body>
    </html>
    """

    success = sender.send_html_email(
        to_emails="recipient@example.com",
        subject="Polymarket Analysis HTML Report",
        html_content=html_content
    )

    return success


def example_email_with_attachments():
    """Send an email with attachments"""
    sender = GmailSender()

    # Create a sample file to attach (if it doesn't exist)
    sample_file = Path("sample_report.txt")
    if not sample_file.exists():
        sample_file.write_text("This is a sample report for Polymarket Analysis")

    success = sender.send_email(
        to_emails=["recipient1@example.com", "recipient2@example.com"],
        subject="Polymarket Report with Attachments",
        body_html="""
        <html>
            <body>
                <h3>Polymarket Analysis Report</h3>
                <p>Please find the attached reports for your review.</p>
                <ul>
                    <li>Market analysis data</li>
                    <li>Performance metrics</li>
                </ul>
            </body>
        </html>
        """,
        body_text="Polymarket Analysis Report - Please find the attached reports.",
        attachments=[str(sample_file)],
        cc_emails="cc@example.com"
    )

    # Clean up sample file
    if sample_file.exists():
        sample_file.unlink()

    return success


def example_using_existing_html():
    """Send email using the existing create_html.py generated content"""
    sender = GmailSender()

    # Check if HTML file exists from create_html.py
    html_file = Path("email/polymarket_report.html")

    if html_file.exists():
        html_content = html_file.read_text(encoding='utf-8')

        success = sender.send_email(
            to_emails="recipient@example.com",
            subject="Polymarket Analysis - Daily Report",
            body_html=html_content,
            body_text="Please view this email in HTML format for the best experience."
        )

        return success
    else:
        print("HTML report file not found. Run create_html.py first.")
        return False


def test_smtp_connection():
    """Test SMTP connection without sending an email"""
    print("Testing Gmail SMTP connection...")

    # Load environment variables
    load_dotenv()

    # Check if required environment variables are set
    if not os.getenv('GMAIL_EMAIL'):
        print("\n❌ GMAIL_EMAIL not set in environment variables")
        print("Please set it in .env file or Railway dashboard")
        return False

    if not os.getenv('GMAIL_APP_PASSWORD'):
        print("\n❌ GMAIL_APP_PASSWORD not set in environment variables")
        print("Please generate an app password at: https://myaccount.google.com/apppasswords")
        return False

    sender = GmailSender()
    success = sender.test_connection()

    if success:
        print("\n✅ SMTP connection successful!")
        print(f"Configured email: {sender.config.sender_email}")
    else:
        print("\n❌ SMTP connection failed")

    return success


def main():
    """Main function to run examples"""
    # Load environment variables
    load_dotenv()

    print("Gmail SMTP Email Sender Examples")
    print("=" * 50)

    # First, test the connection
    if not test_smtp_connection():
        print("\nPlease configure your Gmail credentials before running examples.")
        print("\n1. Copy .env.example to .env")
        print("2. Add your Gmail email address")
        print("3. Generate and add a Gmail App Password")
        return

    print("\nAvailable examples:")
    print("1. Send basic text email")
    print("2. Send HTML email")
    print("3. Send email with attachments")
    print("4. Send email using existing HTML report")
    print("5. Test connection only")
    print("0. Exit")

    while True:
        choice = input("\nSelect an example (0-5): ").strip()

        if choice == "0":
            break
        elif choice == "1":
            print("\nSending basic text email...")
            if example_basic_email():
                print("✅ Email sent successfully!")
            else:
                print("❌ Failed to send email")
        elif choice == "2":
            print("\nSending HTML email...")
            if example_html_email():
                print("✅ Email sent successfully!")
            else:
                print("❌ Failed to send email")
        elif choice == "3":
            print("\nSending email with attachments...")
            if example_email_with_attachments():
                print("✅ Email sent successfully!")
            else:
                print("❌ Failed to send email")
        elif choice == "4":
            print("\nSending email using existing HTML report...")
            if example_using_existing_html():
                print("✅ Email sent successfully!")
            else:
                print("❌ Failed to send email")
        elif choice == "5":
            test_smtp_connection()
        else:
            print("Invalid choice. Please select 0-5.")


if __name__ == "__main__":
    main()