"""
Email Service Module
Handles Gmail IMAP connection and email operations
"""

import imaplib
import email
from email.header import decode_header
from email.utils import parsedate_to_datetime
import re
from datetime import datetime, timedelta
from typing import List, Dict, Tuple, Optional


class EmailService:
    """
    Service for Gmail IMAP operations
    """
    
    def __init__(self):
        """Initialize email service"""
        self.imap = None
        self.connected = False
        self.selected_folder = "INBOX"
        self.email_address = None
    
    def connect(self, email_address: str, password: str) -> Tuple[bool, str]:
        """
        Connect to Gmail via IMAP
        
        Args:
            email_address: Gmail address
            password: App Password (16 characters)
            
        Returns:
            Tuple of (success: bool, message: str)
        """
        try:
            # Add timeout to prevent hanging
            self.imap = imaplib.IMAP4_SSL("imap.gmail.com", port=993, timeout=30)
            
            # Strip whitespace
            email_address = email_address.strip()
            password = password.strip()
            
            # Login
            self.imap.login(email_address, password)
            self.connected = True
            self.email_address = email_address
            
            return True, "Kết nối Gmail thành công!"
            
        except imaplib.IMAP4.error as e:
            error_msg = str(e).lower()
            if 'authentication failed' in error_msg or 'invalid credentials' in error_msg:
                return False, (
                    "❌ Sai email hoặc App Password. Kiểm tra lại:\n"
                    "1. Email đúng định dạng?\n"
                    "2. App Password 16 ký tự (không có dấu cách)?\n"
                    "3. Đã bật IMAP trong Gmail Settings?"
                )
            else:
                return False, f"❌ Lỗi IMAP: {str(e)}"
                
        except Exception as e:
            return False, f"❌ Lỗi kết nối: {str(e)}"
    
    def disconnect(self):
        """Disconnect safely from Gmail"""
        if self.imap:
            try:
                self.imap.close()
            except:
                pass
            try:
                self.imap.logout()
            except:
                pass
        self.imap = None
        self.connected = False
        self.email_address = None
    
    @staticmethod
    def clean_text(text: str) -> str:
        """
        Clean email content
        
        Args:
            text: Raw text
            
        Returns:
            Cleaned text
        """
        if isinstance(text, bytes):
            text = text.decode('utf-8', errors='ignore')
        text = re.sub(r'<[^>]+>', ' ', text)
        text = re.sub(r'\s+', ' ', text)
        return text.strip()
    
    @staticmethod
    def decode_mime_words(s: str) -> str:
        """
        Decode MIME encoded words (Subject, From fields)
        
        Args:
            s: MIME encoded string
            
        Returns:
            Decoded string
        """
        if not s:
            return ""
        try:
            decoded_parts = decode_header(s)
            decoded_string = ""
            for part, encoding in decoded_parts:
                if isinstance(part, bytes):
                    decoded_string += part.decode(encoding or 'utf-8', errors='ignore')
                else:
                    decoded_string += part
            return decoded_string
        except:
            return str(s)
    
    def get_email_body(self, msg) -> str:
        """
        Extract email body content
        
        Args:
            msg: Email message object
            
        Returns:
            Email body text
        """
        body = ""
        
        if msg.is_multipart():
            for part in msg.walk():
                content_type = part.get_content_type()
                content_disposition = str(part.get("Content-Disposition"))

                if "attachment" in content_disposition:
                    continue

                if content_type == "text/plain" and not body:
                    payload = part.get_payload(decode=True)
                    if payload:
                        body = payload.decode('utf-8', errors='ignore')

                elif content_type == "text/html" and not body:
                    payload = part.get_payload(decode=True)
                    if payload:
                        html = payload.decode('utf-8', errors='ignore')
                        body = re.sub(r'<[^>]+>', ' ', html)
                        body = re.sub(r'\s+', ' ', body).strip()

            if not body and msg.get_payload():
                try:
                    part = msg.get_payload()[0]
                    payload = part.get_payload(decode=True)
                    if payload:
                        body = payload.decode('utf-8', errors='ignore')
                except:
                    pass

        else:
            payload = msg.get_payload(decode=True)
            if payload:
                body = payload.decode('utf-8', errors='ignore')

        return self.clean_text(body) if body else "[Không có nội dung]"
    
    @staticmethod
    def escape_html(text: str) -> str:
        """
        Escape HTML special characters
        
        Args:
            text: Raw text
            
        Returns:
            HTML-escaped text
        """
        if not text:
            return ""
        return (str(text)
                .replace("&", "&amp;")
                .replace("<", "&lt;")
                .replace(">", "&gt;")
                .replace('"', "&quot;")
                .replace("'", "&#x27;"))
    
    def fetch_recent_emails(self, limit: int = 20, days_back: int = 60) -> Tuple[Optional[List[Dict]], str]:
        """
        Fetch recent emails from Gmail
        
        Args:
            limit: Maximum number of emails to fetch
            days_back: Number of days to look back
            
        Returns:
            Tuple of (emails list or None, status message)
        """
        if not self.connected or not self.imap:
            return None, "Chưa kết nối Gmail"

        try:
            self.imap.select("INBOX")

            since_date = (datetime.now() - timedelta(days=days_back)).strftime("%d-%b-%Y")
            status, data = self.imap.uid('SEARCH', None, f'SINCE {since_date}')
            
            if status != 'OK':
                return None, "Lỗi tìm kiếm email"

            if not data[0]:
                return [], "Không có email nào trong 60 ngày qua"

            all_uids = data[0].split()
            if len(all_uids) == 0:
                return [], "Không tìm thấy email"

            recent_uids = all_uids[-limit:] if len(all_uids) >= limit else all_uids

            emails = []
            success_count = 0
            error_count = 0
            
            for uid in reversed(recent_uids):
                try:
                    status, msg_data = self.imap.uid('FETCH', uid, '(RFC822)')
                    if status != 'OK' or not msg_data[0]:
                        error_count += 1
                        continue

                    raw_email = msg_data[0][1]
                    msg = email.message_from_bytes(raw_email)

                    subject = self.escape_html(self.decode_mime_words(msg.get("Subject", "(Không có tiêu đề)")))
                    sender = self.escape_html(self.decode_mime_words(msg.get("From", "Không rõ")))
                    date_str = msg.get("Date", "")

                    try:
                        date_obj = parsedate_to_datetime(date_str)
                        date_fmt = date_obj.strftime("%d/%m/%Y %H:%M")
                        date_sort = date_obj
                    except:
                        date_fmt = "Không rõ thời gian"
                        date_sort = datetime.min

                    body = self.get_email_body(msg)

                    emails.append({
                        "uid": uid.decode('utf-8'),
                        "subject": subject,
                        "from": sender,
                        "date": date_fmt,
                        "date_obj": date_sort,
                        "body_preview": self.escape_html(body[:300] + ("..." if len(body) > 300 else "")),
                        "full_body": body
                    })
                    success_count += 1
                    
                except Exception as e:
                    error_count += 1
                    continue

            # Sort by date
            emails.sort(key=lambda x: x.get("date_obj", datetime.min), reverse=True)
            
            # Remove date_obj (used only for sorting)
            for e in emails:
                e.pop("date_obj", None)
            
            result_msg = f"✅ Đã tải thành công {success_count}/{len(recent_uids)} email mới nhất!"
            if error_count > 0:
                result_msg += f" ({error_count} email bị lỗi)"
                
            return emails, result_msg

        except Exception as e:
            return None, f"Lỗi tải email: {str(e)}"
    
    def mark_as_spam(self, uid: str) -> bool:
        """
        Mark email as spam
        
        Args:
            uid: Email UID
            
        Returns:
            Success status
        """
        try:
            self.imap.uid('STORE', uid, '+X-GM-LABELS', '\\Spam')
            return True
        except:
            return False
    
    def add_label(self, uid: str, label: str) -> bool:
        """
        Add label to email
        
        Args:
            uid: Email UID
            label: Label name
            
        Returns:
            Success status
        """
        try:
            self.imap.uid('STORE', uid, '+X-GM-LABELS', label)
            return True
        except:
            return False
