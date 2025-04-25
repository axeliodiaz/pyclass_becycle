"""Module for handling email notifications using Mailtrap (debug) or SendGrid (production)."""

import logging
from abc import ABC, abstractmethod

import aiohttp
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

import settings
from clients.constants import MAILTRAP_API_URL

logger = logging.getLogger(__name__)


class BaseEmailNotifier(ABC):
    """Abstract base class for email notifiers."""

    def __init__(self):
        """Initialize the email notifier with common settings."""
        self.sender_email = settings.EMAIL_SENDER
        self.recipient_emails = settings.EMAIL_RECIPIENTS
        self.subject = settings.EMAIL_SUBJECT

    @abstractmethod
    def validate_config(self) -> bool:
        """Validate that all required email settings are configured."""
        pass

    @abstractmethod
    async def send_email(self, body: str) -> bool:
        """Send an email asynchronously to the specified recipients."""
        pass


class MailtrapEmailNotifier(BaseEmailNotifier):
    """A class to send emails using Mailtrap API (for debugging)."""

    def __init__(self):
        """Initialize the Mailtrap email notifier."""
        super().__init__()
        self.api_token = settings.MAILTRAP_API_TOKEN
        self.api_host = settings.MAILTRAP_API_HOST
        self.inbox_id = settings.MAILTRAP_INBOX_ID

    def validate_config(self) -> bool:
        """Validate that all required Mailtrap settings are configured."""
        return all([
            self.sender_email,
            self.api_token,
            self.api_host,
            self.inbox_id
        ])

    async def send_email(self, body: str) -> bool:
        """
        Send an email using Mailtrap API.

        :param body: Body of the email.
        :return: True if the email was sent successfully, False otherwise.
        """
        if not self.validate_config():
            logger.error("Mailtrap configuration is invalid")
            return False

        url = MAILTRAP_API_URL.format(host=self.api_host, inbox_id=self.inbox_id)

        payload = {
            "from": {
                "email": self.sender_email,
                "name": "Ride Flow"
            },
            "to": [{"email": email} for email in self.recipient_emails],
            "subject": self.subject,
            "html": body,
            "category": "Ride Flow"
        }

        headers = {
            "Authorization": f"Bearer {self.api_token}",
            "Content-Type": "application/json"
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, headers=headers, json=payload) as response:
                    if response.status == 200:
                        logger.info(f"Email sent successfully to {', '.join(self.recipient_emails)}")
                        return True
                    else:
                        error_text = await response.text()
                        logger.error(f"Failed to send email via Mailtrap: {error_text}")
                        return False
        except Exception as e:
            logger.error(f"Failed to send email via Mailtrap: {str(e)}")
            return False


class SendGridEmailNotifier(BaseEmailNotifier):
    """A class to send emails using SendGrid API (for production)."""

    def __init__(self):
        """Initialize the SendGrid email notifier."""
        super().__init__()
        self.api_key = settings.SENDGRID_API_KEY

    def validate_config(self) -> bool:
        """Validate that all required SendGrid settings are configured."""
        return all([
            self.sender_email,
            self.api_key
        ])

    async def send_email(self, body: str) -> bool:
        """
        Send an email using SendGrid API.

        :param body: Body of the email.
        :return: True if the email was sent successfully, False otherwise.
        """
        if not self.validate_config():
            logger.error("SendGrid configuration is invalid")
            return False

        # Create a Mail message using SendGrid's helper classes
        message = Mail(
            from_email=(self.sender_email, "Ride Flow Notifier"),
            to_emails=self.recipient_emails,
            subject=self.subject,
            html_content=body
        )

        try:
            # Create a SendGrid client
            sg = SendGridAPIClient(self.api_key)

            # Send the email
            response = sg.send(message)

            if response.status_code in (200, 202):
                logger.info(f"Email sent successfully to {', '.join(self.recipient_emails)}")
                logger.debug(f"SendGrid response: status_code={response.status_code}, body={response.body}, headers={response.headers}")
                return True
            else:
                logger.error(f"Failed to send email via SendGrid: status_code={response.status_code}, body={response.body}")
                return False
        except Exception as e:
            logger.error(f"Failed to send email via SendGrid: {str(e)}")
            return False


def get_email_notifier():
    """
    Get the appropriate email notifier based on debug settings.

    :return: An instance of BaseEmailNotifier
    """
    if settings.DEBUG:
        return MailtrapEmailNotifier()
    return SendGridEmailNotifier()
