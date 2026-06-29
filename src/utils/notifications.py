"""
Notification system - Send alerts via Email and Telegram
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import logging
from config.config import settings
from typing import Optional
import asyncio

logger = logging.getLogger(__name__)

class NotificationManager:
    """Manager for sending notifications via Email and Telegram"""

    @staticmethod
    def send_email(
        subject: str,
        body: str,
        to_email: Optional[str] = None,
        html: bool = False
    ) -> bool:
        """
        Send email notification

        Args:
            subject: Email subject
            body: Email body
            to_email: Recipient email (default: admin_email from config)
            html: Whether body is HTML or plain text

        Returns:
            True if successful, False otherwise
        """
        try:
            to_email = to_email or settings.admin_email

            # Create email message
            msg = MIMEMultipart("alternative")
            msg["Subject"] = subject
            msg["From"] = settings.smtp_username
            msg["To"] = to_email

            # Attach body
            mime_type = "html" if html else "plain"
            msg.attach(MIMEText(body, mime_type))

            # Send email
            with smtplib.SMTP(settings.smtp_server, settings.smtp_port) as server:
                server.starttls()
                server.login(settings.smtp_username, settings.smtp_password)
                server.send_message(msg)

            logger.info(f"✅ Email sent to {to_email}")
            return True

        except Exception as e:
            logger.error(f"❌ Failed to send email: {str(e)}")
            return False

    @staticmethod
    async def send_telegram(message: str) -> bool:
        """
        Send Telegram notification

        Args:
            message: Message to send

        Returns:
            True if successful, False otherwise
        """
        try:
            if not settings.telegram_bot_token or not settings.telegram_chat_id:
                logger.warning("Telegram credentials not configured")
                return False

            import aiohttp

            url = f"https://api.telegram.org/bot{settings.telegram_bot_token}/sendMessage"
            payload = {
                "chat_id": settings.telegram_chat_id,
                "text": message,
                "parse_mode": "HTML"
            }

            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=payload) as response:
                    if response.status == 200:
                        logger.info("✅ Telegram message sent")
                        return True
                    else:
                        logger.error(f"Telegram API error: {response.status}")
                        return False

        except Exception as e:
            logger.error(f"❌ Failed to send Telegram message: {str(e)}")
            return False


def send_email_notification(subject: str, body: str, html: bool = False) -> bool:
    """Send email notification"""
    return NotificationManager.send_email(subject, body, html=html)


def send_telegram_notification(message: str) -> bool:
    """Send Telegram notification (synchronous wrapper)"""
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    return loop.run_until_complete(NotificationManager.send_telegram(message))
