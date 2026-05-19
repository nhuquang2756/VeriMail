"""
Configuration Loader Module
Handles loading and validation of configuration files
"""

import json
from pathlib import Path
from typing import Dict, Any, Optional


class ConfigLoader:
    """
    Load and manage application configuration
    """
    
    DEFAULT_CONFIG = {
        "email": "",
        "password": "",
        "check_interval": 300,
        "auto_label": True,
        "initial_load": 20,
        "notification_settings": {
            "notify_on_spam": True,
            "notify_on_ham": False
        },
        "advanced_settings": {
            "max_emails_per_check": 50,
            "mark_as_read": False,
            "move_spam_to_folder": False
        }
    }
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize config loader
        
        Args:
            config_path: Path to config file (default: config/config.json)
        """
        if config_path is None:
            project_root = Path(__file__).parent.parent.parent
            config_path = project_root / "config" / "config.json"
        
        self.config_path = Path(config_path)
        self.config = self.load()
    
    def load(self) -> Dict[str, Any]:
        """
        Load configuration from file
        
        Returns:
            Configuration dictionary
        """
        if not self.config_path.exists():
            print(f"⚠️ Config file not found: {self.config_path}")
            print("Using default configuration...")
            return self.DEFAULT_CONFIG.copy()
        
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            # Merge with defaults (in case some keys are missing)
            merged_config = self._merge_with_defaults(config)
            
            return merged_config
            
        except json.JSONDecodeError as e:
            print(f"❌ Error parsing config file: {e}")
            print("Using default configuration...")
            return self.DEFAULT_CONFIG.copy()
        except Exception as e:
            print(f"❌ Error loading config: {e}")
            print("Using default configuration...")
            return self.DEFAULT_CONFIG.copy()
    
    def _merge_with_defaults(self, config: Dict) -> Dict:
        """
        Merge loaded config with defaults
        
        Args:
            config: Loaded configuration
            
        Returns:
            Merged configuration
        """
        merged = self.DEFAULT_CONFIG.copy()
        
        for key, value in config.items():
            if key in merged and isinstance(merged[key], dict) and isinstance(value, dict):
                # Merge nested dictionaries
                merged[key] = {**merged[key], **value}
            else:
                merged[key] = value
        
        return merged
    
    def save(self, config: Optional[Dict] = None):
        """
        Save configuration to file
        
        Args:
            config: Configuration to save (default: current config)
        """
        if config is None:
            config = self.config
        
        # Create directory if not exists
        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=4, ensure_ascii=False)
            print(f"✅ Configuration saved to {self.config_path}")
        except Exception as e:
            print(f"❌ Error saving config: {e}")
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value
        
        Args:
            key: Configuration key (supports dot notation, e.g., 'notification_settings.notify_on_spam')
            default: Default value if key not found
            
        Returns:
            Configuration value
        """
        keys = key.split('.')
        value = self.config
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def set(self, key: str, value: Any):
        """
        Set configuration value
        
        Args:
            key: Configuration key (supports dot notation)
            value: Value to set
        """
        keys = key.split('.')
        config = self.config
        
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        config[keys[-1]] = value
    
    def validate(self) -> bool:
        """
        Validate configuration
        
        Returns:
            True if valid, False otherwise
        """
        # Check required fields
        if not self.config.get('email'):
            print("❌ Email is required in config")
            return False
        
        if not self.config.get('password'):
            print("❌ Password is required in config")
            return False
        
        # Validate email format
        email = self.config.get('email', '')
        if '@' not in email:
            print("❌ Invalid email format")
            return False
        
        # Validate check_interval
        interval = self.config.get('check_interval', 0)
        if not isinstance(interval, int) or interval < 60:
            print("❌ check_interval must be at least 60 seconds")
            return False
        
        return True
