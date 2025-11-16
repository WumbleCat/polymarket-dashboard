"""
SMTP Configuration for Gmail
Handles email configuration and environment variables
"""
import os
from dataclasses import dataclass
from typing import Optional


@dataclass
class SMTPConfig:
    """Configuration for SMTP email sending"""
    smtp_server: str = "smtp.gmail.com"
    smtp_port: int = 587  # TLS port
    sender_email: str = ""
    sender_password: str = ""  # App password for Gmail
    sender_name: Optional[str] = None
    use_tls: bool = True

    @classmethod
    def from_env(cls) -> 'SMTPConfig':
        """Load configuration from environment variables"""
        return cls(
            smtp_server=os.getenv('SMTP_SERVER', 'smtp.gmail.com'),
            smtp_port=int(os.getenv('SMTP_PORT', '587')),
            sender_email=os.getenv('GMAIL_EMAIL', ''),
            sender_password=os.getenv('GMAIL_APP_PASSWORD', ''),
            sender_name=os.getenv('SENDER_NAME', None),
            use_tls=os.getenv('USE_TLS', 'True').lower() == 'true'
        )

    def validate(self) -> bool:
        """Validate that required configuration is present"""
        if not self.sender_email:
            raise ValueError("GMAIL_EMAIL environment variable is required")
        if not self.sender_password:
            raise ValueError("GMAIL_APP_PASSWORD environment variable is required")
        return True