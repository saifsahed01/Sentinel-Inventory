"""
Input Validation Module
Provides validation functions for all user inputs to prevent injection attacks
and enforce business rules.
"""
import re
from typing import Tuple, Optional


class ValidationError(Exception):
    """Custom exception for validation errors."""
    pass


class InputValidator:
    """
    Validates user inputs against security and business rules.
    """
    
    # Business rule constants
    MAX_PRODUCT_NAME_LENGTH = 100
    MAX_USERNAME_LENGTH = 50
    MIN_USERNAME_LENGTH = 3
    MIN_PASSWORD_LENGTH = 8
    MAX_QUANTITY = 1000000
    MAX_PRICE = 1000000.00
    
    # SQL injection patterns to detect
    SQL_INJECTION_PATTERNS = [
        r"(\bOR\b|\bAND\b).*=.*",  # OR/AND with equals
        r"';.*--",  # Comment injection
        r"\bUNION\b.*\bSELECT\b",  # UNION SELECT
        r"\bDROP\b.*\bTABLE\b",  # DROP TABLE
        r"\bINSERT\b.*\bINTO\b",  # INSERT INTO
        r"\bDELETE\b.*\bFROM\b",  # DELETE FROM
        r"\bUPDATE\b.*\bSET\b",  # UPDATE SET
        r"--",  # SQL comments
        r"/\*.*\*/",  # Multi-line comments
        r"xp_.*",  # Extended stored procedures
        r"sp_.*",  # Stored procedures
    ]
    
    @staticmethod
    def validate_product_name(name: str) -> Tuple[bool, Optional[str]]:
        """
        Validate product name.
        
        Args:
            name: Product name to validate
            
        Returns:
            Tuple[bool, Optional[str]]: (is_valid, error_message)
        """
        if not name or not name.strip():
            return False, "Product name cannot be empty"
        
        name = name.strip()
        
        if len(name) > InputValidator.MAX_PRODUCT_NAME_LENGTH:
            return False, f"Product name cannot exceed {InputValidator.MAX_PRODUCT_NAME_LENGTH} characters"
        
        # Check for SQL injection attempts
        if InputValidator._contains_sql_injection(name):
            return False, "Product name contains invalid characters"
        
        # Allow alphanumeric, spaces, hyphens, and common punctuation
        if not re.match(r'^[a-zA-Z0-9\s\-_.,()&]+$', name):
            return False, "Product name contains invalid characters"
        
        return True, None
    
    @staticmethod
    def validate_quantity(quantity: str) -> Tuple[bool, Optional[str], Optional[int]]:
        """
        Validate product quantity.
        
        Args:
            quantity: Quantity as string
            
        Returns:
            Tuple[bool, Optional[str], Optional[int]]: (is_valid, error_message, parsed_value)
        """
        if not quantity or not quantity.strip():
            return False, "Quantity cannot be empty", None
        
        try:
            qty = int(quantity.strip())
        except ValueError:
            return False, "Quantity must be a valid integer", None
        
        if qty < 0:
            return False, "Quantity cannot be negative", None
        
        if qty > InputValidator.MAX_QUANTITY:
            return False, f"Quantity cannot exceed {InputValidator.MAX_QUANTITY}", None
        
        return True, None, qty
    
    @staticmethod
    def validate_price(price: str) -> Tuple[bool, Optional[str], Optional[float]]:
        """
        Validate product price.
        
        Args:
            price: Price as string
            
        Returns:
            Tuple[bool, Optional[str], Optional[float]]: (is_valid, error_message, parsed_value)
        """
        if not price or not price.strip():
            return False, "Price cannot be empty", None
        
        try:
            price_val = float(price.strip())
        except ValueError:
            return False, "Price must be a valid number", None
        
        if price_val < 0:
            return False, "Price cannot be negative", None
        
        if price_val > InputValidator.MAX_PRICE:
            return False, f"Price cannot exceed {InputValidator.MAX_PRICE}", None
        
        # Check for reasonable decimal places (max 2)
        if round(price_val, 2) != price_val:
            return False, "Price can have at most 2 decimal places", None
        
        return True, None, price_val
    
    @staticmethod
    def validate_product_id(product_id: str) -> Tuple[bool, Optional[str], Optional[int]]:
        """
        Validate product ID.
        
        Args:
            product_id: Product ID as string
            
        Returns:
            Tuple[bool, Optional[str], Optional[int]]: (is_valid, error_message, parsed_value)
        """
        if not product_id or not product_id.strip():
            return False, "Product ID cannot be empty", None
        
        try:
            pid = int(product_id.strip())
        except ValueError:
            return False, "Product ID must be a valid integer", None
        
        if pid <= 0:
            return False, "Product ID must be positive", None
        
        return True, None, pid
    
    @staticmethod
    def validate_username(username: str) -> Tuple[bool, Optional[str]]:
        """
        Validate username.
        
        Args:
            username: Username to validate
            
        Returns:
            Tuple[bool, Optional[str]]: (is_valid, error_message)
        """
        if not username or not username.strip():
            return False, "Username cannot be empty"
        
        username = username.strip()
        
        if len(username) < InputValidator.MIN_USERNAME_LENGTH:
            return False, f"Username must be at least {InputValidator.MIN_USERNAME_LENGTH} characters"
        
        if len(username) > InputValidator.MAX_USERNAME_LENGTH:
            return False, f"Username cannot exceed {InputValidator.MAX_USERNAME_LENGTH} characters"
        
        # Check for SQL injection attempts
        if InputValidator._contains_sql_injection(username):
            return False, "Username contains invalid characters"
        
        # Allow only alphanumeric and underscore
        if not re.match(r'^[a-zA-Z0-9_]+$', username):
            return False, "Username can only contain letters, numbers, and underscores"
        
        return True, None
    
    @staticmethod
    def validate_password(password: str) -> Tuple[bool, Optional[str]]:
        """
        Validate password strength.
        
        Args:
            password: Password to validate
            
        Returns:
            Tuple[bool, Optional[str]]: (is_valid, error_message)
        """
        if not password:
            return False, "Password cannot be empty"
        
        if len(password) < InputValidator.MIN_PASSWORD_LENGTH:
            return False, f"Password must be at least {InputValidator.MIN_PASSWORD_LENGTH} characters"
        
        # Check for at least one uppercase, one lowercase, and one digit
        if not re.search(r'[A-Z]', password):
            return False, "Password must contain at least one uppercase letter"
        
        if not re.search(r'[a-z]', password):
            return False, "Password must contain at least one lowercase letter"
        
        if not re.search(r'\d', password):
            return False, "Password must contain at least one digit"
        
        return True, None
    
    @staticmethod
    def validate_search_term(search_term: str) -> Tuple[bool, Optional[str]]:
        """
        Validate search term to prevent SQL injection.
        
        Args:
            search_term: Search term to validate
            
        Returns:
            Tuple[bool, Optional[str]]: (is_valid, error_message)
        """
        if not search_term or not search_term.strip():
            return False, "Search term cannot be empty"
        
        search_term = search_term.strip()
        
        # Check for SQL injection attempts
        if InputValidator._contains_sql_injection(search_term):
            return False, "Search term contains invalid characters"
        
        # Allow alphanumeric, spaces, and basic punctuation
        if not re.match(r'^[a-zA-Z0-9\s\-_.]+$', search_term):
            return False, "Search term contains invalid characters"
        
        return True, None
    
    @staticmethod
    def _contains_sql_injection(input_str: str) -> bool:
        """
        Check if input contains potential SQL injection patterns.
        
        Args:
            input_str: String to check
            
        Returns:
            bool: True if potential SQL injection detected
        """
        input_upper = input_str.upper()
        
        for pattern in InputValidator.SQL_INJECTION_PATTERNS:
            if re.search(pattern, input_upper, re.IGNORECASE):
                return True
        
        return False
    
    @staticmethod
    def sanitize_input(input_str: str) -> str:
        """
        Sanitize input by removing potentially dangerous characters.
        This is a fallback - parameterized queries are the primary defense.
        
        Args:
            input_str: String to sanitize
            
        Returns:
            str: Sanitized string
        """
        if not input_str:
            return ""
        
        # Remove null bytes
        sanitized = input_str.replace('\x00', '')
        
        # Remove control characters except newline and tab
        sanitized = ''.join(char for char in sanitized if ord(char) >= 32 or char in '\n\t')
        
        return sanitized.strip()


def validate_and_parse_product_data(name: str, quantity: str, price: str) -> Tuple[bool, Optional[str], Optional[dict]]:
    """
    Validate all product data at once.
    
    Args:
        name: Product name
        quantity: Product quantity as string
        price: Product price as string
        
    Returns:
        Tuple[bool, Optional[str], Optional[dict]]: (is_valid, error_message, parsed_data)
    """
    # Validate name
    valid, error = InputValidator.validate_product_name(name)
    if not valid:
        return False, error, None
    
    # Validate quantity
    valid, error, qty = InputValidator.validate_quantity(quantity)
    if not valid:
        return False, error, None
    
    # Validate price
    valid, error, price_val = InputValidator.validate_price(price)
    if not valid:
        return False, error, None
    
    return True, None, {
        'name': name.strip(),
        'quantity': qty,
        'price': price_val
    }

# Made with Bob
