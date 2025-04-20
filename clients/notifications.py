"""Module for handling email notifications using SMTP (Gmail or Mailtrap) or Mailtrap API."""

import ssl
from email.message import EmailMessage

import aiohttp
import aiosmtplib

import settings


class EmailNotifier:
    """
    A class to send emails asynchronously using SMTP (Gmail or Mailtrap) or Mailtrap API.
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
        self.use_mailtrap_api = settings.USE_MAILTRAP_API
        self.mailtrap_api_token = settings.MAILTRAP_API_TOKEN
        self.mailtrap_api_host = settings.MAILTRAP_API_HOST
        self.mailtrap_inbox_id = settings.MAILTRAP_INBOX_ID

    def validate_config(self) -> bool:
        """Validate that all required email settings are configured."""
        if self.use_mailtrap_api:
            return all([
                self.sender_email,
                self.mailtrap_api_token,
                self.mailtrap_api_host,
                self.mailtrap_inbox_id
            ])
        return all([
            self.sender_email,
            self.sender_password,
            self.smtp_server,
            self.port
        ])

    async def send_email(self, body: str) -> bool:
        """
        Send an email asynchronously to the specified recipients.

        :param body: Body of the email.
        :return: True if the email was sent successfully, False otherwise.
        """
        if not self.validate_config():
            print("Email configuration is invalid")
            return False

        if self.use_mailtrap_api:
            return await self._send_email_api(body)
        return await self._send_email_smtp(body)

    async def _send_email_api(self, body: str) -> bool:
        """
        Send an email using Mailtrap API.

        :param body: Body of the email.
        :return: True if the email was sent successfully, False otherwise.
        """
        url = f"https://{self.mailtrap_api_host}/api/send/{self.mailtrap_inbox_id}"
        
        payload = {
            "from": {
                "email": self.sender_email,
                "name": "Becycle Notifier"
            },
            "to": [{"email": email} for email in self.recipient_emails],
            "subject": self.subject,
            "text": body,
            "category": "Becycle Schedule"
        }

        headers = {
            "Authorization": f"Bearer {self.mailtrap_api_token}",
            "Content-Type": "application/json"
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, headers=headers, json=payload) as response:
                    if response.status == 200:
                        print(f"Email sent successfully to {', '.join(self.recipient_emails)}")
                        return True
                    else:
                        error_text = await response.text()
                        print(f"Failed to send email via API: {error_text}")
                        return False
        except Exception as e:
            print(f"Failed to send email via API: {str(e)}")
            return False

    async def _send_email_smtp(self, body: str) -> bool:
        """
        Send an email using SMTP.

        :param body: Body of the email.
        :return: True if the email was sent successfully, False otherwise.
        """
        msg = EmailMessage()
        msg["From"] = self.sender_email
        msg["To"] = ", ".join(self.recipient_emails)
        msg["Subject"] = self.subject
        msg.set_content(body)

        try:
            # Create SSL context
            context = ssl.create_default_context()
            
            # Connect to SMTP server
            smtp = aiosmtplib.SMTP(
                hostname=self.smtp_server,
                port=self.port,
                use_tls=True,
                tls_context=context
            )
            
            await smtp.connect()
            await smtp.login(self.sender_email, self.sender_password)
            await smtp.send_message(msg)
            await smtp.quit()
            
            print(f"Email sent successfully to {', '.join(self.recipient_emails)}")
            return True
            
        except Exception as e:
            print(f"Failed to send email via SMTP: {str(e)}")
            return False
