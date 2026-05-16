"""
Logging Module
Provides structured logging with different levels and outputs to both file and console.
"""
import logging
import os
from datetime import datetime
from typing import Optional


class AppLogger:
    """
    Application logger with structured logging to file and console.
    """
    
    def __init__(self, name: str = "InventorySystem", log_dir: str = "logs"):
        """
        Initialize the logger.
        
        Args:
            name: Logger name
            log_dir: Directory to store log files
        """
        self.name = name
        self.log_dir = log_dir
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)
        
        # Create logs directory if it doesn't exist
        # Handle serverless environments where filesystem may be read-only
        try:
            if not os.path.exists(log_dir):
                os.makedirs(log_dir, exist_ok=True)
        except (OSError, PermissionError) as e:
            # In serverless, fall back to console-only logging
            print(f"Warning: Could not create log directory, using console-only logging: {e}")
            self.log_dir = None
        
        # Prevent duplicate handlers
        if not self.logger.handlers:
            self._setup_handlers()
    
    def _setup_handlers(self):
        """Setup file and console handlers with formatters."""
        
        # Create formatters
        detailed_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        simple_formatter = logging.Formatter(
            '%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # Only add file handlers if log directory is available (not in serverless)
        if self.log_dir:
            try:
                # File handler for all logs
                log_file = os.path.join(self.log_dir, f"app_{datetime.now().strftime('%Y%m%d')}.log")
                file_handler = logging.FileHandler(log_file, encoding='utf-8')
                file_handler.setLevel(logging.DEBUG)
                file_handler.setFormatter(detailed_formatter)
                self.logger.addHandler(file_handler)
                
                # File handler for errors only
                error_log_file = os.path.join(self.log_dir, f"errors_{datetime.now().strftime('%Y%m%d')}.log")
                error_file_handler = logging.FileHandler(error_log_file, encoding='utf-8')
                error_file_handler.setLevel(logging.ERROR)
                error_file_handler.setFormatter(detailed_formatter)
                self.logger.addHandler(error_file_handler)
            except (OSError, PermissionError) as e:
                print(f"Warning: Could not create file handlers: {e}")
        
        # Console handler (always available)
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(simple_formatter)
        self.logger.addHandler(console_handler)
    
    def debug(self, message: str, context: Optional[dict] = None):
        """
        Log debug message.
        
        Args:
            message: Log message
            context: Additional context dictionary
        """
        if context:
            message = f"{message} | Context: {context}"
        self.logger.debug(message)
    
    def info(self, message: str, context: Optional[dict] = None):
        """
        Log info message.
        
        Args:
            message: Log message
            context: Additional context dictionary
        """
        if context:
            message = f"{message} | Context: {context}"
        self.logger.info(message)
    
    def warning(self, message: str, context: Optional[dict] = None):
        """
        Log warning message.
        
        Args:
            message: Log message
            context: Additional context dictionary
        """
        if context:
            message = f"{message} | Context: {context}"
        self.logger.warning(message)
    
    def error(self, message: str, context: Optional[dict] = None, exc_info: bool = False):
        """
        Log error message.
        
        Args:
            message: Log message
            context: Additional context dictionary
            exc_info: Include exception information
        """
        if context:
            message = f"{message} | Context: {context}"
        self.logger.error(message, exc_info=exc_info)
    
    def critical(self, message: str, context: Optional[dict] = None, exc_info: bool = False):
        """
        Log critical message.
        
        Args:
            message: Log message
            context: Additional context dictionary
            exc_info: Include exception information
        """
        if context:
            message = f"{message} | Context: {context}"
        self.logger.critical(message, exc_info=exc_info)
    
    def log_authentication(self, username: str, success: bool, reason: Optional[str] = None):
        """
        Log authentication attempt.
        
        Args:
            username: Username attempting authentication
            success: Whether authentication was successful
            reason: Reason for failure if applicable
        """
        if success:
            self.info(f"Authentication successful", {'username': username})
        else:
            self.warning(
                f"Authentication failed",
                {'username': username, 'reason': reason or 'Invalid credentials'}
            )
    
    def log_database_operation(self, operation: str, table: str, success: bool, details: Optional[dict] = None):
        """
        Log database operation.
        
        Args:
            operation: Type of operation (SELECT, INSERT, UPDATE, DELETE)
            table: Table name
            success: Whether operation was successful
            details: Additional details
        """
        context = {'operation': operation, 'table': table}
        if details:
            context.update(details)
        
        if success:
            self.debug(f"Database operation completed", context)
        else:
            self.error(f"Database operation failed", context)
    
    def log_validation_error(self, field: str, value: str, error: str):
        """
        Log validation error.
        
        Args:
            field: Field name that failed validation
            value: Value that was validated (sanitized for logging)
            error: Validation error message
        """
        # Sanitize value for logging (truncate if too long)
        safe_value = value[:50] + '...' if len(value) > 50 else value
        self.warning(
            f"Validation error",
            {'field': field, 'value': safe_value, 'error': error}
        )
    
    def log_security_event(self, event_type: str, details: dict, severity: str = "WARNING"):
        """
        Log security-related event.
        
        Args:
            event_type: Type of security event
            details: Event details
            severity: Severity level (INFO, WARNING, ERROR, CRITICAL)
        """
        message = f"Security event: {event_type}"
        
        if severity == "INFO":
            self.info(message, details)
        elif severity == "WARNING":
            self.warning(message, details)
        elif severity == "ERROR":
            self.error(message, details)
        elif severity == "CRITICAL":
            self.critical(message, details)
    
    def log_business_operation(self, operation: str, user: str, details: Optional[dict] = None):
        """
        Log business operation (add product, update quantity, etc.).
        
        Args:
            operation: Type of business operation
            user: User performing the operation
            details: Operation details
        """
        context = {'operation': operation, 'user': user}
        if details:
            context.update(details)
        
        self.info(f"Business operation: {operation}", context)


# Global logger instance
_global_logger: Optional[AppLogger] = None


def get_logger(name: str = "InventorySystem", log_dir: str = "logs") -> AppLogger:
    """
    Get or create the global logger instance.
    
    Args:
        name: Logger name
        log_dir: Directory to store log files
        
    Returns:
        AppLogger: Logger instance
    """
    global _global_logger
    if _global_logger is None:
        _global_logger = AppLogger(name, log_dir)
    return _global_logger


def reset_logger():
    """Reset the global logger instance (useful for testing)."""
    global _global_logger
    _global_logger = None

# Made with Bob
