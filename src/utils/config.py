"""
Configuration Module
Manages application configuration from environment variables and .env files.
"""
import os
from typing import Optional
from dotenv import load_dotenv


class Config:
    """
    Application configuration manager.
    Loads configuration from environment variables with sensible defaults.
    """
    
    def __init__(self, env_file: str = ".env"):
        """
        Initialize configuration.
        
        Args:
            env_file: Path to .env file
        """
        # Load environment variables from .env file if it exists
        if os.path.exists(env_file):
            load_dotenv(env_file)
        
        # Database configuration
        self.DATABASE_PATH = os.getenv("DATABASE_PATH", "data/inventory.db")
        
        # Authentication configuration
        self.SESSION_TIMEOUT_MINUTES = int(os.getenv("SESSION_TIMEOUT_MINUTES", "30"))
        self.MAX_LOGIN_ATTEMPTS = int(os.getenv("MAX_LOGIN_ATTEMPTS", "5"))
        self.BCRYPT_ROUNDS = int(os.getenv("BCRYPT_ROUNDS", "12"))
        
        # Validation configuration
        self.MAX_PRODUCT_NAME_LENGTH = int(os.getenv("MAX_PRODUCT_NAME_LENGTH", "100"))
        self.MAX_USERNAME_LENGTH = int(os.getenv("MAX_USERNAME_LENGTH", "50"))
        self.MIN_USERNAME_LENGTH = int(os.getenv("MIN_USERNAME_LENGTH", "3"))
        self.MIN_PASSWORD_LENGTH = int(os.getenv("MIN_PASSWORD_LENGTH", "8"))
        self.MAX_QUANTITY = int(os.getenv("MAX_QUANTITY", "1000000"))
        self.MAX_PRICE = float(os.getenv("MAX_PRICE", "1000000.00"))
        
        # Business rules
        self.LOW_STOCK_THRESHOLD = int(os.getenv("LOW_STOCK_THRESHOLD", "5"))
        
        # Logging configuration
        self.LOG_DIRECTORY = os.getenv("LOG_DIRECTORY", "logs")
        self.LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
        
        # Application configuration
        self.APP_NAME = os.getenv("APP_NAME", "Inventory Management System")
        self.APP_VERSION = os.getenv("APP_VERSION", "2.0.0")
        self.DEBUG_MODE = os.getenv("DEBUG_MODE", "False").lower() == "true"
        
        # Ensure required directories exist
        self._ensure_directories()
    
    def _ensure_directories(self):
        """Create required directories if they don't exist."""
        # Create database directory
        db_dir = os.path.dirname(self.DATABASE_PATH)
        if db_dir and not os.path.exists(db_dir):
            os.makedirs(db_dir)
        
        # Create log directory
        if not os.path.exists(self.LOG_DIRECTORY):
            os.makedirs(self.LOG_DIRECTORY)
    
    def get_database_path(self) -> str:
        """Get the database file path."""
        return self.DATABASE_PATH
    
    def get_session_timeout(self) -> int:
        """Get session timeout in minutes."""
        return self.SESSION_TIMEOUT_MINUTES
    
    def get_max_login_attempts(self) -> int:
        """Get maximum login attempts before lockout."""
        return self.MAX_LOGIN_ATTEMPTS
    
    def get_bcrypt_rounds(self) -> int:
        """Get bcrypt hashing rounds."""
        return self.BCRYPT_ROUNDS
    
    def get_low_stock_threshold(self) -> int:
        """Get low stock threshold."""
        return self.LOW_STOCK_THRESHOLD
    
    def get_log_directory(self) -> str:
        """Get log directory path."""
        return self.LOG_DIRECTORY
    
    def is_debug_mode(self) -> bool:
        """Check if debug mode is enabled."""
        return self.DEBUG_MODE
    
    def to_dict(self) -> dict:
        """
        Convert configuration to dictionary.
        Excludes sensitive information.
        
        Returns:
            dict: Configuration dictionary
        """
        return {
            'app_name': self.APP_NAME,
            'app_version': self.APP_VERSION,
            'database_path': self.DATABASE_PATH,
            'session_timeout_minutes': self.SESSION_TIMEOUT_MINUTES,
            'max_login_attempts': self.MAX_LOGIN_ATTEMPTS,
            'low_stock_threshold': self.LOW_STOCK_THRESHOLD,
            'log_directory': self.LOG_DIRECTORY,
            'debug_mode': self.DEBUG_MODE
        }
    
    def __repr__(self) -> str:
        """String representation of configuration."""
        return f"Config(app={self.APP_NAME}, version={self.APP_VERSION}, debug={self.DEBUG_MODE})"


# Global configuration instance
_global_config: Optional[Config] = None


def get_config(env_file: str = ".env") -> Config:
    """
    Get or create the global configuration instance.
    
    Args:
        env_file: Path to .env file
        
    Returns:
        Config: Configuration instance
    """
    global _global_config
    if _global_config is None:
        _global_config = Config(env_file)
    return _global_config


def reset_config():
    """Reset the global configuration instance (useful for testing)."""
    global _global_config
    _global_config = None


def create_default_env_file(path: str = ".env.example"):
    """
    Create a default .env.example file with all configuration options.
    
    Args:
        path: Path where to create the example file
    """
    content = """# Database Configuration
DATABASE_PATH=data/inventory.db

# Authentication Configuration
SESSION_TIMEOUT_MINUTES=30
MAX_LOGIN_ATTEMPTS=5
BCRYPT_ROUNDS=12

# Validation Configuration
MAX_PRODUCT_NAME_LENGTH=100
MAX_USERNAME_LENGTH=50
MIN_USERNAME_LENGTH=3
MIN_PASSWORD_LENGTH=8
MAX_QUANTITY=1000000
MAX_PRICE=1000000.00

# Business Rules
LOW_STOCK_THRESHOLD=5

# Logging Configuration
LOG_DIRECTORY=logs
LOG_LEVEL=INFO

# Application Configuration
APP_NAME=Inventory Management System
APP_VERSION=2.0.0
DEBUG_MODE=False
"""
    
    with open(path, 'w') as f:
        f.write(content)
    
    print(f"Created example environment file: {path}")

# Made with Bob
