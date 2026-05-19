"""
AI Spam Detector - Auto Email Checker Entry Point
Background service for automatic email monitoring

Run: python auto_checker.py
"""

import sys
from pathlib import Path

# Add src to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Import and run the auto checker service
from src.services.auto_checker_service import AutoCheckerService

if __name__ == "__main__":
    print("🚀 Starting Auto Email Checker (Refactored Version)...\n")
    service = AutoCheckerService()
    service.run()

