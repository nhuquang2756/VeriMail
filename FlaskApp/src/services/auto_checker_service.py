"""
Auto Checker Service Module
Background service for automatic email monitoring and spam detection
"""

import time
from datetime import datetime
from typing import Tuple, List, Dict
import sys

from src.services import EmailService, NotificationService
from src.core import ModelManager
from src.utils import ConfigLoader, setup_logger

logger = setup_logger('auto_checker')


class AutoCheckerService:
    """
    Automatic email checker service
    Monitors Gmail inbox and detects spam in real-time
    """
    
    def __init__(self, config_path: str = None):
        """
        Initialize auto checker service
        
        Args:
            config_path: Path to config file
        """
        logger.info("Initializing Auto Checker Service...")
        
        # Default configuration
        self.config_dict = {
            'email': '',
            'password': '',
            'check_interval': 300,
            'initial_load': 20,
            'model_to_use': 'Voting Classifier',
            'auto_label': True,
            'notification_settings': {
                'notify_on_spam': True,
                'notify_on_ham': False,
                'telegram_token': '',
                'telegram_chat_id': ''
            }
        }
        
        # Load configuration from file
        try:
            from src.utils import ConfigLoader
            config_loader = ConfigLoader(config_path)
            
            # Copy values from ConfigLoader to dict
            for key in ['email', 'password', 'check_interval', 'initial_load', 'model_to_use', 'auto_label']:
                val = config_loader.get(key)
                if val is not None:
                    self.config_dict[key] = val
            
            # Handle nested notification_settings
            notify_spam = config_loader.get('notification_settings.notify_on_spam')
            notify_ham = config_loader.get('notification_settings.notify_on_ham')
            telegram_token = config_loader.get('notification_settings.telegram_token')
            telegram_chat_id = config_loader.get('notification_settings.telegram_chat_id')
            
            if notify_spam is not None:
                self.config_dict['notification_settings']['notify_on_spam'] = notify_spam
            if notify_ham is not None:
                self.config_dict['notification_settings']['notify_on_ham'] = notify_ham
            if telegram_token is not None:
                self.config_dict['notification_settings']['telegram_token'] = telegram_token
            if telegram_chat_id is not None:
                self.config_dict['notification_settings']['telegram_chat_id'] = telegram_chat_id
                
            logger.info("Config loaded successfully")
            
        except Exception as e:
            logger.warning(f"Could not load config: {e}. Using defaults.")
            print(f"⚠️ Using default config (please setup config/config.json)")
        
        # Initialize services
        self.email_service = EmailService()
        self.model_manager = ModelManager()
        
        # Initialize notification service
        telegram_token = self.config_dict['notification_settings'].get('telegram_token', '')
        telegram_chat_id = self.config_dict['notification_settings'].get('telegram_chat_id', '')
        self.notification_service = NotificationService(telegram_token, telegram_chat_id)
        
        # State
        self.connected = False
        self.last_checked_id = None
        self.initial_load_done = False
        
        logger.info("Auto Checker Service initialized successfully")
    
    def get_config(self, key: str, default=None):
        """Helper to get config value with dot notation support"""
        keys = key.split('.')
        value = self.config_dict
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
            else:
                return default
        return value if value is not None else default
    
    def connect(self) -> bool:
        """
        Connect to Gmail
        
        Returns:
            Success status
        """
        email = self.get_config('email')
        password = self.get_config('password')
        
        if not email or not password:
            logger.error("Email or password not configured")
            return False
        
        success, msg = self.email_service.connect(email, password)
        self.connected = success
        
        if success:
            logger.info(f"Connected to Gmail: {email}")
        else:
            logger.error(f"Failed to connect: {msg}")
        
        return success
    
    def check_initial_emails(self) -> Tuple[int, int]:
        """
        Load and analyze initial batch of emails
        
        Returns:
            Tuple of (total_count, spam_count)
        """
        logger.info("Loading initial emails...")
        
        initial_load = self.get_config('initial_load', 20)
        emails, msg = self.email_service.fetch_recent_emails(limit=initial_load)
        
        if emails is None:
            logger.error(f"Failed to fetch emails: {msg}")
            return 0, 0
        
        if not emails:
            logger.info("No emails found")
            return 0, 0
        
        print("=" * 70)
        print(f"📊 ANALYZING {len(emails)} INITIAL EMAILS...")
        print("=" * 70)
        sys.stdout.flush()
        
        model_name = self.get_config('model_to_use', 'Voting Classifier')
        total_count = 0
        spam_count = 0
        spam_list = []
        
        for idx, email_data in enumerate(emails, 1):
            if idx % 5 == 0:
                print(f"⏳ Processing: {idx}/{len(emails)} emails...")
                sys.stdout.flush()
            
            try:
                # Predict
                prediction = self.model_manager.predict_single(
                    email_data['full_body'], 
                    model_name
                )
                
                total_count += 1
                
                if prediction == 'spam':
                    spam_count += 1
                    spam_list.append({
                        'from': email_data['from'],
                        'subject': email_data['subject'],
                        'date': email_data['date']
                    })
                
            except Exception as e:
                logger.error(f"Error analyzing email {idx}: {e}")
                continue
        
        # Display results
        print("\n" + "=" * 70)
        print("✅ INITIAL ANALYSIS COMPLETED")
        print("=" * 70)
        print(f"📊 Total: {total_count} emails")
        print(f"🚫 Spam: {spam_count} emails ({spam_count*100//total_count if total_count > 0 else 0}%)")
        print(f"✅ Ham: {total_count - spam_count} emails")
        sys.stdout.flush()
        
        # Display spam list
        if spam_list:
            print("\n" + "-" * 70)
            print("🚫 SPAM EMAILS DETECTED:")
            print("-" * 70)
            for i, spam in enumerate(spam_list, 1):
                print(f"\n{i}. 📨 From: {spam['from']}")
                print(f"   📌 Subject: {spam['subject']}")
                print(f"   📅 Date: {spam['date']}")
            print("-" * 70)
            sys.stdout.flush()
        
        print("=" * 70)
        print("🔄 Switching to real-time monitoring...\n")
        sys.stdout.flush()
        
        self.initial_load_done = True
        logger.info(f"Initial analysis completed: {total_count} emails, {spam_count} spam")
        
        return total_count, spam_count
    
    def check_new_emails(self) -> Tuple[int, int]:
        """
        Check for new unread emails
        
        Returns:
            Tuple of (new_count, spam_count)
        """
        # For now, use a simple approach - fetch recent emails
        # In production, you'd use IMAP IDLE or similar
        
        emails, msg = self.email_service.fetch_recent_emails(limit=10)
        
        if emails is None or not emails:
            return 0, 0
        
        model_name = self.get_config('model_to_use', 'Voting Classifier')
        new_count = 0
        spam_count = 0
        
        notify_spam = self.get_config('notification_settings.notify_on_spam', True)
        notify_ham = self.get_config('notification_settings.notify_on_ham', False)
        
        spam_list = []
        ham_list = []
        
        for email_data in emails:
            try:
                prediction = self.model_manager.predict_single(
                    email_data['full_body'],
                    model_name
                )
                
                new_count += 1
                
                if prediction == 'spam':
                    spam_count += 1
                    spam_list.append(email_data)
                    
                    # Send notification
                    if notify_spam and self.notification_service.enabled:
                        self.notification_service.notify_spam_detected(
                            email_data['subject'],
                            email_data['from'],
                            email_data['date']
                        )
                else:
                    ham_list.append(email_data)
                    
                    if notify_ham and self.notification_service.enabled:
                        self.notification_service.notify_ham_verified(
                            email_data['subject'],
                            email_data['from'],
                            email_data['date']
                        )
                
            except Exception as e:
                logger.error(f"Error checking email: {e}")
                continue
        
        # Display results
        if new_count > 0:
            print("\n" + "=" * 70)
            print("📬 NEW EMAILS DETECTED!")
            print("=" * 70)
            print(f"📊 Total: {new_count} new emails ({spam_count} spam, {len(ham_list)} ham)")
            sys.stdout.flush()
            
            if spam_list and notify_spam:
                print("\n" + "-" * 70)
                print("🚫 SPAM EMAILS:")
                print("-" * 70)
                for i, spam in enumerate(spam_list, 1):
                    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    print(f"\n{i}. 🚫 [{timestamp}] SPAM DETECTED")
                    print(f"   📨 From: {spam['from']}")
                    print(f"   📌 Subject: {spam['subject']}")
                    print(f"   📅 Date: {spam['date']}")
                print("-" * 70)
                sys.stdout.flush()
            
            print("=" * 70 + "\n")
            sys.stdout.flush()
        
        return new_count, spam_count
    
    def run(self):
        """
        Run the auto checker service
        """
        print("=" * 70)
        print("🛡️  AUTO EMAIL SPAM CHECKER - STARTED")
        print("=" * 70)
        print(f"📧 Email: {self.get_config('email', '<unknown>')}")
        print(f"🤖 Model: {self.get_config('model_to_use', 'Voting Classifier')}")
        print(f"⏱️  Check interval: {self.get_config('check_interval', 300)}s")
        print(f"🏷️  Auto label: {'Enabled' if self.get_config('auto_label', True) else 'Disabled'}")
        print(f"🔔 Telegram: {'Enabled' if self.notification_service.enabled else 'Disabled'}")
        print("=" * 70)
        print()
        sys.stdout.flush()
        
        # Connect to Gmail
        if not self.connect():
            print("❌ Cannot connect to Gmail. Check config!")
            sys.stdout.flush()
            return
        
        print("✅ Connected to Gmail successfully!\n")
        sys.stdout.flush()
        
        # Send start notification
        if self.notification_service.enabled:
            self.notification_service.notify_service_started()
        
        # Step 1: Load initial emails
        print("🚀 STEP 1: LOADING INITIAL EMAILS\n")
        sys.stdout.flush()
        initial_total, initial_spam = self.check_initial_emails()
        
        # Step 2: Real-time monitoring
        print("📡 STEP 2: REAL-TIME MONITORING")
        print("💡 Press Ctrl+C to stop\n")
        sys.stdout.flush()
        
        check_count = 0
        total_emails_realtime = 0
        total_spam_realtime = 0
        check_interval = self.get_config('check_interval', 300)
        
        try:
            while True:
                check_count += 1
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                
                try:
                    # Check for new emails
                    new_count, spam_count = self.check_new_emails()
                    
                    if new_count > 0:
                        total_emails_realtime += new_count
                        total_spam_realtime += spam_count
                        print(f"📈 Real-time stats: {total_emails_realtime} emails ({total_spam_realtime} spam)\n")
                        sys.stdout.flush()
                    else:
                        print(f"[{timestamp}] 🔍 Check #{check_count}: No new emails")
                        sys.stdout.flush()
                    
                    # Wait before next check
                    print(f"⏳ Waiting {check_interval}s before next check...")
                    sys.stdout.flush()
                    time.sleep(check_interval)
                    
                except Exception as e:
                    logger.error(f"Error in check cycle: {e}")
                    print(f"⚠️ Error: {e}")
                    print("Retrying in 60s...")
                    sys.stdout.flush()
                    time.sleep(60)
                    
                    # Try to reconnect
                    if not self.connect():
                        print("❌ Cannot reconnect. Will keep trying...")
                        sys.stdout.flush()
        
        except KeyboardInterrupt:
            print("\n\n" + "=" * 70)
            print("🛑 AUTO EMAIL CHECKER STOPPED")
            print("=" * 70)
            print(f"📊 Initial load: {initial_total} emails ({initial_spam} spam)")
            print(f"📊 Real-time: {check_count} checks")
            print(f"📧 Total detected (real-time): {total_emails_realtime} ({total_spam_realtime} spam)")
            print("=" * 70 + "\n")
            sys.stdout.flush()
            
            self.email_service.disconnect()
            logger.info("Service stopped by user")
        
        except Exception as e:
            logger.error(f"Critical error: {e}")
            print(f"\n❌ Critical error: {e}")
            sys.stdout.flush()
            self.email_service.disconnect()


def main():
    """Main entry point"""
    service = AutoCheckerService()
    service.run()


if __name__ == "__main__":
    main()
