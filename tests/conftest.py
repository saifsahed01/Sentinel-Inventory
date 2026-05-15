"""
Pytest Configuration and Shared Fixtures
Provides mock database connections and test data setup for all test modules.
"""
import pytest
from unittest.mock import Mock, MagicMock, patch
from datetime import datetime
import bcrypt


@pytest.fixture
def mock_db():
    """
    Create a mock DatabaseManager instance.
    
    Returns:
        Mock: Mocked DatabaseManager with common methods
    """
    db = Mock()
    db.connect = Mock(return_value=True)
    db.close = Mock()
    db.execute_query = Mock(return_value=True)
    db.fetch_one = Mock(return_value=None)
    db.fetch_all = Mock(return_value=[])
    db.initialize_database = Mock(return_value=True)
    return db


@pytest.fixture
def mock_validator():
    """
    Create a mock InputValidator instance.
    
    Returns:
        Mock: Mocked InputValidator with validation methods
    """
    validator = Mock()
    # Default successful validation responses
    validator.validate_product_name = Mock(return_value=(True, None))
    validator.validate_quantity = Mock(return_value=(True, None, 10))
    validator.validate_price = Mock(return_value=(True, None, 99.99))
    validator.validate_product_id = Mock(return_value=(True, None, 1))
    validator.validate_search_term = Mock(return_value=(True, None))
    return validator


@pytest.fixture
def mock_logger():
    """
    Create a mock AppLogger instance.
    
    Returns:
        Mock: Mocked AppLogger with logging methods
    """
    logger = Mock()
    logger.info = Mock()
    logger.debug = Mock()
    logger.warning = Mock()
    logger.error = Mock()
    logger.log_validation_error = Mock()
    logger.log_business_operation = Mock()
    return logger


@pytest.fixture
def mock_config():
    """
    Create a mock Config instance.
    
    Returns:
        Mock: Mocked Config with configuration methods
    """
    config = Mock()
    config.get_low_stock_threshold = Mock(return_value=10)
    return config


@pytest.fixture
def sample_user_data():
    """
    Provide sample user data for testing.
    
    Returns:
        dict: Sample user credentials and information
    """
    return {
        'username': 'testuser',
        'password': 'TestPass123!',
        'role': 'admin',
        'password_hash': bcrypt.hashpw('TestPass123!'.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    }


@pytest.fixture
def sample_product_data():
    """
    Provide sample product data for testing.
    
    Returns:
        dict: Sample product information
    """
    return {
        'id': 1,
        'name': 'Test Product',
        'quantity': 100,
        'price': 49.99,
        'category': 'Electronics',
        'created_at': datetime.now().isoformat(),
        'updated_at': datetime.now().isoformat()
    }


@pytest.fixture
def sample_product_row():
    """
    Provide sample product database row for testing.
    
    Returns:
        tuple: Sample product row as returned from database
    """
    timestamp = datetime.now().isoformat()
    return (1, 'Test Product', 100, 49.99, 'Electronics', timestamp, timestamp)


@pytest.fixture
def multiple_product_rows():
    """
    Provide multiple sample product rows for testing.
    
    Returns:
        list: List of product row tuples
    """
    timestamp = datetime.now().isoformat()
    return [
        (1, 'Product A', 50, 19.99, 'Category1', timestamp, timestamp),
        (2, 'Product B', 30, 29.99, 'Category2', timestamp, timestamp),
        (3, 'Product C', 5, 39.99, 'Category1', timestamp, timestamp),
    ]


@pytest.fixture
def cleanup_test_db():
    """
    Fixture to clean up test database after tests.
    Yields control to test, then performs cleanup.
    """
    yield
    # Cleanup code would go here if using real database
    # For mocked tests, this is a placeholder


@pytest.fixture
def mock_session_data():
    """
    Provide sample session data for authentication testing.
    
    Returns:
        dict: Sample session information
    """
    return {
        'session_id': 'test_session_123',
        'username': 'testuser',
        'created_at': datetime.now(),
        'last_activity': datetime.now()
    }


@pytest.fixture
def auth_manager_with_mocks(mock_db):
    """
    Create an AuthenticationManager instance with mocked database.
    
    Args:
        mock_db: Mocked database fixture
        
    Returns:
        AuthenticationManager: Instance with mocked dependencies
    """
    from src.logic.auth import AuthenticationManager
    return AuthenticationManager(mock_db)


@pytest.fixture
def inventory_manager_with_mocks(mock_db, mock_validator, mock_logger, mock_config):
    """
    Create an InventoryManager instance with all mocked dependencies.
    
    Args:
        mock_db: Mocked database fixture
        mock_validator: Mocked validator fixture
        mock_logger: Mocked logger fixture
        mock_config: Mocked config fixture
        
    Returns:
        InventoryManager: Instance with mocked dependencies
    """
    from src.logic.inventory import InventoryManager
    
    # Mock the _ensure_schema method to avoid database calls during initialization
    with patch.object(InventoryManager, '_ensure_schema'):
        manager = InventoryManager(mock_db, mock_validator, mock_logger, mock_config)
    
    return manager

# Made with Bob
