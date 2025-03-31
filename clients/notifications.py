"""Module for handling email notifications using Gmail SMTP."""

from email.message import EmailMessage
from typing import List

import ssl
import aiosmtplib

import settings


class EmailNotifier:
    """
    A class to send emails asynchronously using a Gmail account.
    """

    def __init__(self):
        """
        Initialize the email notifier with the sender's credentials.
        """
        self.sender_email = settings.EMAIL_SENDER
        self.sender_password = settings.EMAIL_PASSWORD
        self.smtp_server = settings.SMTP_SERVER
        self.port = settings.SMTP_PORT
        self.subject = settings.EMAIL_SUBJECT
        self.recipient_emails = settings.EMAIL_RECIPIENTS

    def validate_config(self) -> bool:
        """Validate that all required email settings are configured."""
        return all(
            [self.sender_email, self.sender_password, self.smtp_server, self.port]
        )

    async def send_email(self, body: str) -> bool:
        """
        Send an email asynchronously to the specified recipients.

        :param body: Body of the email.
        :return: True if the email was sent successfully, False otherwise.
        """
        if not self.validate_config():
            print("Email configuration is invalid")
            return False

        msg = EmailMessage()
        msg["From"] = self.sender_email
        msg["To"] = ", ".join(self.recipient_emails)
        msg["Subject"] = self.subject
        msg.set_content(body)

        context = ssl.create_default_context()

        try:
            await aiosmtplib.send(
                msg,
                hostname=self.smtp_server,
                port=self.port,
                username=self.sender_email,
                password=self.sender_password,
                use_tls=True,
                tls_context=context,
            )
        except aiosmtplib.SMTPException as e:
            print(f"Error sending email: {e}")
            return False

        return True
