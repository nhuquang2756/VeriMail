"""
Validation Module
Input validation utilities
"""

import re
from typing import Tuple


def validate_email(email: str) -> Tuple[bool, str]:
    """
    Validate email address format
    
    Args:
        email: Email address to validate
        
    Returns:
        Tuple of (is_valid: bool, message: str)
    """
    if not email:
        return False, "Email không được để trống"
    
    email = email.strip()
    
    # Basic email regex
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    
    if not re.match(email_pattern, email):
        return False, "Email không đúng định dạng"
    
    # Check for Gmail specifically if needed
    if '@gmail.com' not in email.lower():
        return False, "Chỉ hỗ trợ Gmail (@gmail.com)"
    
    return True, "Email hợp lệ"


def validate_app_password(password: str) -> Tuple[bool, str]:
    """
    Validate Gmail App Password
    
    Args:
        password: App Password to validate
        
    Returns:
        Tuple of (is_valid: bool, message: str)
    """
    if not password:
        return False, "App Password không được để trống"
    
    # Remove all spaces
    password = password.replace(" ", "").strip()
    
    # App Password should be 16 characters
    if len(password) != 16:
        return False, f"App Password phải có đúng 16 ký tự (hiện tại: {len(password)})"
    
    # Should be alphanumeric
    if not password.isalnum():
        return False, "App Password chỉ chứa chữ và số"
    
    return True, "App Password hợp lệ"


def validate_text(text: str, min_length: int = 1, max_length: int = 10000) -> Tuple[bool, str]:
    """
    Validate text input
    
    Args:
        text: Text to validate
        min_length: Minimum text length
        max_length: Maximum text length
        
    Returns:
        Tuple of (is_valid: bool, message: str)
    """
    if not text:
        return False, "Văn bản không được để trống"
    
    text = text.strip()
    
    if len(text) < min_length:
        return False, f"Văn bản phải có ít nhất {min_length} ký tự"
    
    if len(text) > max_length:
        return False, f"Văn bản không được vượt quá {max_length} ký tự"
    
    return True, "Văn bản hợp lệ"


def validate_model_name(model_name: str, available_models: list) -> Tuple[bool, str]:
    """
    Validate model name
    
    Args:
        model_name: Model name to validate
        available_models: List of available model names
        
    Returns:
        Tuple of (is_valid: bool, message: str)
    """
    if not model_name:
        return False, "Tên model không được để trống"
    
    if model_name not in available_models:
        return False, f"Model '{model_name}' không tồn tại. Available: {', '.join(available_models)}"
    
    return True, "Model hợp lệ"


def sanitize_input(text: str) -> str:
    """
    Sanitize user input to prevent injection attacks
    
    Args:
        text: Input text
        
    Returns:
        Sanitized text
    """
    if not text:
        return ""
    
    # Remove potentially dangerous characters
    text = text.strip()
    
    # Remove null bytes
    text = text.replace('\x00', '')
    
    return text
