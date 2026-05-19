"""
Notification Service Module
Handles Telegram and email notifications
"""

import requests
from typing import Optional, Tuple
from src.utils import setup_logger

logger = setup_logger('notification_service')


class NotificationService:
    """
    Service for sending notifications via Telegram
    """
    
    def __init__(self, telegram_token: Optional[str] = None, telegram_chat_id: Optional[str] = None):
        """
        Initialize notification service
        
        Args:
            telegram_token: Telegram bot token
            telegram_chat_id: Telegram chat ID
        """
        self.telegram_token = telegram_token
        self.telegram_chat_id = telegram_chat_id
        self.enabled = bool(telegram_token and telegram_chat_id)
    
    def send_telegram(self, message: str) -> Tuple[bool, str]:
        """
        Send message via Telegram
        
        Args:
            message: Message to send
            
        Returns:
            Tuple of (success: bool, message: str)
        """
        if not self.enabled:
            logger.warning("Telegram notifications not configured")
            return False, "Telegram not configured"
        
        try:
            url = f"https://api.telegram.org/bot{self.telegram_token}/sendMessage"
            data = {
                "chat_id": self.telegram_chat_id,
                "text": message,
                "parse_mode": "HTML"
            }
            
            response = requests.post(url, data=data, timeout=10)
            
            if response.status_code == 200:
                logger.info("Telegram notification sent successfully")
                return True, "Notification sent"
            else:
                logger.error(f"Telegram API error: {response.status_code}")
                return False, f"API error: {response.status_code}"
                
        except requests.exceptions.Timeout:
            logger.error("Telegram request timeout")
            return False, "Request timeout"
        except Exception as e:
            logger.error(f"Error sending Telegram notification: {e}")
            return False, str(e)
    
    def notify_spam_detected(self, subject: str, sender: str, date: str) -> Tuple[bool, str]:
        """
        Send spam detection notification
        
        Args:
            subject: Email subject
            sender: Email sender
            date: Email date
            
        Returns:
            Tuple of (success: bool, message: str)
        """
        message = f"""
🚨 <b>SPAM DETECTED!</b>

📧 <b>Subject:</b> {subject[:100]}
👤 <b>From:</b> {sender[:100]}
📅 <b>Date:</b> {date}

⚠️ This email has been marked as spam by AI.
        """.strip()
        
        return self.send_telegram(message)
    
    def notify_ham_verified(self, subject: str, sender: str, date: str) -> Tuple[bool, str]:
        """
        Send ham verification notification
        
        Args:
            subject: Email subject
            sender: Email sender
            date: Email date
            
        Returns:
            Tuple of (success: bool, message: str)
        """
        message = f"""
✅ <b>HAM VERIFIED</b>

📧 <b>Subject:</b> {subject[:100]}
👤 <b>From:</b> {sender[:100]}
📅 <b>Date:</b> {date}

✓ This email appears to be legitimate.
        """.strip()
        
        return self.send_telegram(message)
    
    def notify_service_started(self) -> Tuple[bool, str]:
        """
        Send service started notification
        
        Returns:
            Tuple of (success: bool, message: str)
        """
        message = """
🚀 <b>Auto Email Checker Started</b>

The spam detection service is now running.
You will receive notifications when spam is detected.
        """.strip()
        
        return self.send_telegram(message)
    
    def notify_error(self, error_message: str) -> Tuple[bool, str]:
        """
        Send error notification
        
        Args:
            error_message: Error message
            
        Returns:
            Tuple of (success: bool, message: str)
        """
        message = f"""
❌ <b>Error Occurred</b>

{error_message}
        """.strip()
        
        return self.send_telegram(message)
