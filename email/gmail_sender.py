"""
Gmail SMTP Email Sender
Handles sending emails through Gmail's SMTP server
"""
import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from typing import List, Optional, Union
from pathlib import Path
import logging

from smtp_config import SMTPConfig


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class GmailSender:
    """Gmail SMTP email sender with attachment support"""

    def __init__(self, config: Optional[SMTPConfig] = None):
        """Initialize with SMTP configuration"""
        self.config = config or SMTPConfig.from_env()
        self.config.validate()

    def send_email(
        self,
        to_emails: Union[str, List[str]],
        subject: str,
        body_text: Optional[str] = None,
        body_html: Optional[str] = None,
        attachments: Optional[List[str]] = None,
        cc_emails: Optional[Union[str, List[str]]] = None,
        bcc_emails: Optional[Union[str, List[str]]] = None,
        reply_to: Optional[str] = None
    ) -> bool:
        """
        Send email with optional HTML content and attachments

        Args:
            to_emails: Recipient email(s)
            subject: Email subject
            body_text: Plain text body
            body_html: HTML body (optional)
            attachments: List of file paths to attach
            cc_emails: CC recipients
            bcc_emails: BCC recipients
            reply_to: Reply-to address

        Returns:
            True if email sent successfully, False otherwise
        """
        try:
            # Convert single email to list
            if isinstance(to_emails, str):
                to_emails = [to_emails]
            if isinstance(cc_emails, str):
                cc_emails = [cc_emails]
            if isinstance(bcc_emails, str):
                bcc_emails = [bcc_emails]

            # Create message
            message = MIMEMultipart('alternative')
            message['Subject'] = subject
            message['From'] = f"{self.config.sender_name or 'Polymarket Analysis'} <{self.config.sender_email}>"
            message['To'] = ', '.join(to_emails)

            if cc_emails:
                message['Cc'] = ', '.join(cc_emails)
            if reply_to:
                message['Reply-To'] = reply_to

            # Add text and HTML parts
            if body_text:
                text_part = MIMEText(body_text, 'plain', 'utf-8')
                message.attach(text_part)

            if body_html:
                html_part = MIMEText(body_html, 'html', 'utf-8')
                message.attach(html_part)
            elif not body_text:
                # If no content provided, add default text
                text_part = MIMEText('(No content)', 'plain', 'utf-8')
                message.attach(text_part)

            # Add attachments
            if attachments:
                for file_path in attachments:
                    self._attach_file(message, file_path)

            # Combine all recipients
            all_recipients = list(to_emails)
            if cc_emails:
                all_recipients.extend(cc_emails)
            if bcc_emails:
                all_recipients.extend(bcc_emails)

            # Send email
            return self._send_message(message, all_recipients)

        except Exception as e:
            logger.error(f"Failed to send email: {str(e)}")
            return False

    def _attach_file(self, message: MIMEMultipart, file_path: str) -> None:
        """Attach a file to the email message"""
        path = Path(file_path)
        if not path.exists():
            logger.warning(f"Attachment file not found: {file_path}")
            return

        try:
            with open(path, 'rb') as file:
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(file.read())

            encoders.encode_base64(part)
            part.add_header(
                'Content-Disposition',
                f'attachment; filename= {path.name}'
            )
            message.attach(part)
            logger.info(f"Attached file: {path.name}")

        except Exception as e:
            logger.error(f"Failed to attach file {file_path}: {str(e)}")

    def _send_message(self, message: MIMEMultipart, recipients: List[str]) -> bool:
        """Send the email message via SMTP"""
        import socket
        import os

        # Check if running in Railway with network restrictions
        if os.getenv('RAILWAY_ENVIRONMENT'):
            logger.warning("Running in Railway environment - SMTP may be restricted")
            logger.warning("Railway's free tier blocks outbound SMTP connections (port 587/465)")
            logger.warning("Consider upgrading to Railway's paid tier or using an email API service instead")

        context = ssl.create_default_context()

        try:
            # Test network connectivity first
            socket.create_connection((self.config.smtp_server, self.config.smtp_port), timeout=5)

            with smtplib.SMTP(self.config.smtp_server, self.config.smtp_port) as server:
                server.set_debuglevel(0)  # Set to 1 for debugging

                if self.config.use_tls:
                    server.starttls(context=context)

                server.login(self.config.sender_email, self.config.sender_password)

                text = message.as_string()
                server.sendmail(
                    self.config.sender_email,
                    recipients,
                    text
                )

            logger.info(f"Email sent successfully to {', '.join(recipients)}")
            return True

        except socket.error as e:
            if "Network is unreachable" in str(e) or e.errno == 101:
                logger.error("Network is unreachable - SMTP ports may be blocked")
                logger.error("If running on Railway free tier, SMTP is blocked. Solutions:")
                logger.error("1. Upgrade to Railway paid tier (Team plan or higher)")
                logger.error("2. Use an email API service (SendGrid, Mailgun, etc.)")
                logger.error("3. Run the script locally instead")
            else:
                logger.error(f"Network error: {str(e)}")
            return False
        except smtplib.SMTPAuthenticationError:
            logger.error("SMTP Authentication failed. Check your email and app password.")
            return False
        except smtplib.SMTPException as e:
            logger.error(f"SMTP error: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error sending email: {str(e)}")
            return False

    def send_html_email(
        self,
        to_emails: Union[str, List[str]],
        subject: str,
        html_content: str,
        attachments: Optional[List[str]] = None
    ) -> bool:
        """
        Convenience method to send HTML email

        Args:
            to_emails: Recipient email(s)
            subject: Email subject
            html_content: HTML content
            attachments: Optional file attachments

        Returns:
            True if successful
        """
        return self.send_email(
            to_emails=to_emails,
            subject=subject,
            body_html=html_content,
            attachments=attachments
        )

    def test_connection(self) -> bool:
        """Test SMTP connection and authentication"""
        context = ssl.create_default_context()

        try:
            logger.info(f"Testing connection to {self.config.smtp_server}:{self.config.smtp_port}")

            with smtplib.SMTP(self.config.smtp_server, self.config.smtp_port) as server:
                server.set_debuglevel(0)

                if self.config.use_tls:
                    server.starttls(context=context)

                server.login(self.config.sender_email, self.config.sender_password)

            logger.info("SMTP connection test successful!")
            return True

        except smtplib.SMTPAuthenticationError:
            logger.error("Authentication failed. Check your Gmail email and app password.")
            logger.error("Make sure you're using an App Password, not your regular Gmail password.")
            logger.error("Enable 2FA and generate an App Password at: https://myaccount.google.com/apppasswords")
            return False
        except Exception as e:
            logger.error(f"Connection test failed: {str(e)}")
            return False