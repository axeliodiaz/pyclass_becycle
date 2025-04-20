"""Module for handling email notifications using Mailtrap (debug) or Mandrill (production)."""

from abc import ABC, abstractmethod
import logging
import aiohttp

import settings
from clients.constants import MAILTRAP_API_URL, MANDRILL_API_URL

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
                "name": "Becycle Notifier"
            },
            "to": [{"email": email} for email in self.recipient_emails],
            "subject": self.subject,
            "text": body,
            "category": "Becycle Schedule"
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


class MandrillEmailNotifier(BaseEmailNotifier):
    """A class to send emails using Mandrill API (for production)."""

    def __init__(self):
        """Initialize the Mandrill email notifier."""
        super().__init__()
        self.api_key = settings.MANDRILL_API_KEY

    def validate_config(self) -> bool:
        """Validate that all required Mandrill settings are configured."""
        return all([
            self.sender_email,
            self.api_key
        ])

    async def send_email(self, body: str) -> bool:
        """
        Send an email using Mandrill API.

        :param body: Body of the email.
        :return: True if the email was sent successfully, False otherwise.
        """
        if not self.validate_config():
            logger.error("Mandrill configuration is invalid")
            return False

        payload = {
            "key": self.api_key,
            "message": {
                "from_email": self.sender_email,
                "to": [{"email": email} for email in self.recipient_emails],
                "subject": self.subject,
                "text": body,
                "headers": {
                    "Reply-To": self.sender_email
                }
            }
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(MANDRILL_API_URL, json=payload) as response:
                    if response.status == 200:
                        result = await response.json()
                        if all(msg.get('status') == 'sent' for msg in result):
                            logger.info(f"Email sent successfully to {', '.join(self.recipient_emails)}")
                            return True
                        else:
                            logger.error(f"Failed to send email via Mandrill: {result}")
                            return False
                    else:
                        error_text = await response.text()
                        logger.error(f"Failed to send email via Mandrill: {error_text}")
                        return False
        except Exception as e:
            logger.error(f"Failed to send email via Mandrill: {str(e)}")
            return False


def get_email_notifier():
    """
    Get the appropriate email notifier based on debug settings.
    
    :return: An instance of BaseEmailNotifier
    """
    if settings.DEBUG:
        return MailtrapEmailNotifier()
    return MandrillEmailNotifier()
