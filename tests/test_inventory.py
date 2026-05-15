"""
Unit Tests for InventoryManager
Tests inventory operations, validation, error handling, and edge cases.
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

from src.logic.inventory import (
    InventoryManager,
    Product,
    ProductNotFoundError,
    DuplicateProductError,
    InvalidProductDataError
)


class TestProduct:
    """Test suite for Product class."""
    
    def test_should_create_product_with_valid_data(self):
        """
        Test that Product can be created with valid data.
        Validates basic product instantiation.
        """
        product = Product(
            name="Test Product",
            quantity=100,
            price=49.99,
            category="Electronics"
        )
        
        assert product.name == "Test Product"
        assert product.quantity == 100
        assert product.price == 49.99
        assert product.category == "Electronics"
    
    def test_should_reject_negative_quantity(self):
        """
        Test that Product rejects negative quantity (edge case).
        Validates quantity validation logic.
        """
        with pytest.raises(InvalidProductDataError) as exc_info:
            Product(name="Test", quantity=-5, price=10.0)
        
        assert "Quantity cannot be negative" in str(exc_info.value)
    
    def test_should_reject_negative_price(self):
        """
        Test that Product rejects negative price (edge case).
        Validates price validation logic.
        """
        with pytest.raises(InvalidProductDataError) as exc_info:
            Product(name="Test", quantity=10, price=-5.0)
        
        assert "Price cannot be negative" in str(exc_info.value)
    
    def test_should_accept_zero_quantity(self):
        """
        Test that Product accepts zero quantity (edge case).
        Validates that out-of-stock items can be represented.
        """
        product = Product(name="Test", quantity=0, price=10.0)
        
        assert product.quantity == 0
    
    def test_should_accept_zero_price(self):
        """
        Test that Product accepts zero price (edge case).
        Validates that free items can be represented.
        """
        product = Product(name="Test", quantity=10, price=0.0)
        
        assert product.price == 0.0
    
    def test_should_convert_to_dict(self, sample_product_data):
        """
        Test that Product can be converted to dictionary.
        Validates serialization functionality.
        """
        product = Product(
            name=sample_product_data['name'],
            quantity=sample_product_data['quantity'],
            price=sample_product_data['price'],
            category=sample_product_data['category'],
            product_id=sample_product_data['id']
        )
        
        product_dict = product.to_dict()
        
        assert product_dict['name'] == sample_product_data['name']
        assert product_dict['quantity'] == sample_product_data['quantity']
        assert product_dict['price'] == sample_product_data['price']
        assert product_dict['category'] == sample_product_data['category']
    
    def test_should_create_from_db_row(self, sample_product_row):
        """
        Test that Product can be created from database row.
        Validates database deserialization.
        """
        product = Product.from_db_row(sample_product_row)
        
        assert product.id == sample_product_row[0]
        assert product.name == sample_product_row[1]
        assert product.quantity == sample_product_row[2]
        assert product.price == sample_product_row[3]


class TestInventoryManager:
    """Test suite for InventoryManager class."""
    
    def test_should_initialize_with_dependencies(self, mock_db, mock_validator, mock_logger, mock_config):
        """
        Test that InventoryManager initializes with all dependencies.
        Validates proper dependency injection.
        """
        with patch.object(InventoryManager, '_ensure_schema'):
            manager = InventoryManager(mock_db, mock_validator, mock_logger, mock_config)
        
        assert manager.db == mock_db
        assert manager.validator == mock_validator
        assert manager.logger == mock_logger
        assert manager.config == mock_config
    
    def test_should_add_valid_product_successfully(self, inventory_manager_with_mocks, sample_product_row):
        """
        Test adding a valid product to inventory.
        Validates successful product creation with all validations passing.
        """
        manager = inventory_manager_with_mocks
        
        # Mock validator responses
        manager.validator.validate_product_name.return_value = (True, None)
        manager.validator.validate_quantity.return_value = (True, None, 100)
        manager.validator.validate_price.return_value = (True, None, 49.99)
        
        # Mock database responses
        manager.db.fetch_one.side_effect = [
            None,  # No duplicate check
            sample_product_row  # Return newly created product
        ]
        manager.db.execute_query.return_value = True
        
        product = manager.add_product("Test Product", "100", "49.99", "Electronics")
        
        assert product is not None
        assert product.name == "Test Product"
        assert product.quantity == 100
        assert product.price == 49.99
    
    def test_should_reject_duplicate_product_name(self, inventory_manager_with_mocks):
        """
        Test that adding a duplicate product name fails.
        Validates duplicate prevention logic.
        """
        manager = inventory_manager_with_mocks
        
        # Mock validator responses
        manager.validator.validate_product_name.return_value = (True, None)
        manager.validator.validate_quantity.return_value = (True, None, 100)
        manager.validator.validate_price.return_value = (True, None, 49.99)
        
        # Mock database to return existing product
        manager.db.fetch_one.return_value = (1,)  # Product exists
        
        with pytest.raises(DuplicateProductError) as exc_info:
            manager.add_product("Existing Product", "100", "49.99")
        
        assert "already exists" in str(exc_info.value)
    
    def test_should_reject_invalid_product_name(self, inventory_manager_with_mocks):
        """
        Test that invalid product name is rejected (edge case).
        Validates input validation for product names.
        """
        manager = inventory_manager_with_mocks
        
        # Mock validator to reject name
        manager.validator.validate_product_name.return_value = (False, "Name too short")
        
        with pytest.raises(InvalidProductDataError) as exc_info:
            manager.add_product("", "100", "49.99")
        
        assert "Invalid product name" in str(exc_info.value)
    
    def test_should_reject_invalid_quantity(self, inventory_manager_with_mocks):
        """
        Test that invalid quantity is rejected (edge case).
        Validates quantity validation.
        """
        manager = inventory_manager_with_mocks
        
        # Mock validator responses
        manager.validator.validate_product_name.return_value = (True, None)
        manager.validator.validate_quantity.return_value = (False, "Invalid quantity", None)
        
        with pytest.raises(InvalidProductDataError) as exc_info:
            manager.add_product("Test Product", "invalid", "49.99")
        
        assert "Invalid quantity" in str(exc_info.value)
    
    def test_should_reject_invalid_price(self, inventory_manager_with_mocks):
        """
        Test that invalid price is rejected (edge case).
        Validates price validation.
        """
        manager = inventory_manager_with_mocks
        
        # Mock validator responses
        manager.validator.validate_product_name.return_value = (True, None)
        manager.validator.validate_quantity.return_value = (True, None, 100)
        manager.validator.validate_price.return_value = (False, "Invalid price", None)
        
        with pytest.raises(InvalidProductDataError) as exc_info:
            manager.add_product("Test Product", "100", "invalid")
        
        assert "Invalid price" in str(exc_info.value)
    
    def test_should_update_product_quantity(self, inventory_manager_with_mocks, sample_product_row):
        """
        Test updating product quantity.
        Validates quantity update functionality.
        """
        manager = inventory_manager_with_mocks
        
        # Mock validator responses
        manager.validator.validate_product_id.return_value = (True, None, 1)
        manager.validator.validate_quantity.return_value = (True, None, 150)
        
        # Mock database responses
        updated_row = list(sample_product_row)
        updated_row[2] = 150  # Update quantity
        manager.db.fetch_one.side_effect = [
            sample_product_row,  # Existing product
            tuple(updated_row)  # Updated product
        ]
        manager.db.execute_query.return_value = True
        
        product = manager.update_product("1", quantity="150")
        
        assert product.quantity == 150
    
    def test_should_update_product_price(self, inventory_manager_with_mocks, sample_product_row):
        """
        Test updating product price.
        Validates price update functionality.
        """
        manager = inventory_manager_with_mocks
        
        # Mock validator responses
        manager.validator.validate_product_id.return_value = (True, None, 1)
        manager.validator.validate_price.return_value = (True, None, 59.99)
        
        # Mock database responses
        updated_row = list(sample_product_row)
        updated_row[3] = 59.99  # Update price
        manager.db.fetch_one.side_effect = [
            sample_product_row,  # Existing product
            tuple(updated_row)  # Updated product
        ]
        manager.db.execute_query.return_value = True
        
        product = manager.update_product("1", price="59.99")
        
        assert product.price == 59.99
    
    def test_should_fail_update_for_nonexistent_product(self, inventory_manager_with_mocks):
        """
        Test that updating non-existent product fails (edge case).
        Validates error handling for missing products.
        """
        manager = inventory_manager_with_mocks
        
        # Mock validator responses
        manager.validator.validate_product_id.return_value = (True, None, 999)
        
        # Mock database to return no product
        manager.db.fetch_one.return_value = None
        
        with pytest.raises(ProductNotFoundError) as exc_info:
            manager.update_product("999", quantity="100")
        
        assert "not found" in str(exc_info.value)
    
    def test_should_delete_product_successfully(self, inventory_manager_with_mocks):
        """
        Test deleting a product from inventory.
        Validates product removal functionality.
        """
        manager = inventory_manager_with_mocks
        
        # Mock validator responses
        manager.validator.validate_product_id.return_value = (True, None, 1)
        
        # Mock database responses
        manager.db.fetch_one.return_value = ("Test Product",)  # Product exists
        manager.db.execute_query.return_value = True
        
        result = manager.delete_product("1")
        
        assert result is True
    
    def test_should_fail_delete_for_nonexistent_product(self, inventory_manager_with_mocks):
        """
        Test that deleting non-existent product fails (edge case).
        Validates error handling for missing products.
        """
        manager = inventory_manager_with_mocks
        
        # Mock validator responses
        manager.validator.validate_product_id.return_value = (True, None, 999)
        
        # Mock database to return no product
        manager.db.fetch_one.return_value = None
        
        with pytest.raises(ProductNotFoundError) as exc_info:
            manager.delete_product("999")
        
        assert "not found" in str(exc_info.value)
    
    def test_should_search_products_by_name(self, inventory_manager_with_mocks, multiple_product_rows):
        """
        Test searching for products by name.
        Validates search functionality.
        """
        manager = inventory_manager_with_mocks
        
        # Mock validator responses
        manager.validator.validate_search_term.return_value = (True, None)
        
        # Mock database to return matching products
        manager.db.fetch_all.return_value = [multiple_product_rows[0]]
        
        products = manager.search_products("Product A")
        
        assert len(products) == 1
        assert products[0].name == "Product A"
    
    def test_should_search_products_by_category(self, inventory_manager_with_mocks, multiple_product_rows):
        """
        Test searching for products by category.
        Validates category-based search.
        """
        manager = inventory_manager_with_mocks
        
        # Mock validator responses
        manager.validator.validate_search_term.return_value = (True, None)
        
        # Mock database to return matching products
        matching_products = [row for row in multiple_product_rows if row[4] == "Category1"]
        manager.db.fetch_all.return_value = matching_products
        
        products = manager.search_products("Category1")
        
        assert len(products) == 2
        assert all(p.category == "Category1" for p in products)
    
    def test_should_return_empty_list_for_no_matches(self, inventory_manager_with_mocks):
        """
        Test that search returns empty list when no matches found (edge case).
        Validates handling of no results.
        """
        manager = inventory_manager_with_mocks
        
        # Mock validator responses
        manager.validator.validate_search_term.return_value = (True, None)
        
        # Mock database to return no products
        manager.db.fetch_all.return_value = []
        
        products = manager.search_products("NonexistentProduct")
        
        assert len(products) == 0
        assert isinstance(products, list)
    
    def test_should_get_product_by_id(self, inventory_manager_with_mocks, sample_product_row):
        """
        Test retrieving a product by ID.
        Validates single product retrieval.
        """
        manager = inventory_manager_with_mocks
        
        # Mock validator responses
        manager.validator.validate_product_id.return_value = (True, None, 1)
        
        # Mock database response
        manager.db.fetch_one.return_value = sample_product_row
        
        product = manager.get_product_by_id("1")
        
        assert product.id == 1
        assert product.name == "Test Product"
    
    def test_should_fail_get_product_for_invalid_id(self, inventory_manager_with_mocks):
        """
        Test that getting product with invalid ID fails (edge case).
        Validates ID validation.
        """
        manager = inventory_manager_with_mocks
        
        # Mock validator to reject ID
        manager.validator.validate_product_id.return_value = (False, "Invalid ID", None)
        
        with pytest.raises(InvalidProductDataError) as exc_info:
            manager.get_product_by_id("invalid")
        
        assert "Invalid product ID" in str(exc_info.value)
    
    def test_should_get_all_products(self, inventory_manager_with_mocks, multiple_product_rows):
        """
        Test retrieving all products.
        Validates bulk product retrieval.
        """
        manager = inventory_manager_with_mocks
        
        # Mock database response
        manager.db.fetch_all.return_value = multiple_product_rows
        
        products = manager.get_all_products()
        
        assert len(products) == 3
        assert all(isinstance(p, Product) for p in products)
    
    def test_should_return_empty_list_when_no_products(self, inventory_manager_with_mocks):
        """
        Test that getting all products returns empty list when inventory is empty (edge case).
        Validates handling of empty inventory.
        """
        manager = inventory_manager_with_mocks
        
        # Mock database to return no products
        manager.db.fetch_all.return_value = []
        
        products = manager.get_all_products()
        
        assert len(products) == 0
        assert isinstance(products, list)
    
    def test_should_get_low_stock_products(self, inventory_manager_with_mocks, multiple_product_rows):
        """
        Test retrieving low stock products.
        Validates low stock filtering.
        """
        manager = inventory_manager_with_mocks
        
        # Mock database to return low stock products
        low_stock = [multiple_product_rows[2]]  # Product C has quantity 5
        manager.db.fetch_all.return_value = low_stock
        
        products = manager.get_low_stock_products(threshold=10)
        
        assert len(products) == 1
        assert products[0].quantity < 10
    
    def test_should_use_config_threshold_for_low_stock(self, inventory_manager_with_mocks):
        """
        Test that low stock uses config threshold when not provided.
        Validates configuration integration.
        """
        manager = inventory_manager_with_mocks
        
        # Mock config threshold
        manager.config.get_low_stock_threshold.return_value = 15
        
        # Mock database response
        manager.db.fetch_all.return_value = []
        
        manager.get_low_stock_products()
        
        # Verify database was called with config threshold
        call_args = manager.db.fetch_all.call_args
        assert call_args[0][1] == (15,)
    
    def test_should_calculate_inventory_value(self, inventory_manager_with_mocks):
        """
        Test calculating total inventory value.
        Validates inventory valuation calculation.
        """
        manager = inventory_manager_with_mocks
        
        # Mock database to return total value
        manager.db.fetch_one.return_value = (5000.50,)
        
        total_value = manager.get_inventory_value()
        
        assert total_value == 5000.50
    
    def test_should_return_zero_for_empty_inventory_value(self, inventory_manager_with_mocks):
        """
        Test that inventory value is zero when empty (edge case).
        Validates handling of empty inventory valuation.
        """
        manager = inventory_manager_with_mocks
        
        # Mock database to return None
        manager.db.fetch_one.return_value = (None,)
        
        total_value = manager.get_inventory_value()
        
        assert total_value == 0.0
    
    def test_should_export_to_csv_successfully(self, inventory_manager_with_mocks, multiple_product_rows, tmp_path):
        """
        Test exporting inventory to CSV file.
        Validates CSV export functionality.
        """
        manager = inventory_manager_with_mocks
        
        # Mock database response
        manager.db.fetch_all.return_value = multiple_product_rows
        
        # Create temporary file path
        csv_file = tmp_path / "test_export.csv"
        
        result = manager.export_to_csv(str(csv_file))
        
        assert result is True
        assert csv_file.exists()
    
    def test_should_handle_csv_export_error(self, inventory_manager_with_mocks):
        """
        Test that CSV export handles errors gracefully (edge case).
        Validates error handling in export functionality.
        """
        manager = inventory_manager_with_mocks
        
        # Mock database to raise exception
        manager.db.fetch_all.side_effect = Exception("Database error")
        
        result = manager.export_to_csv("/invalid/path/file.csv")
        
        assert result is False
    
    def test_should_reject_invalid_search_term(self, inventory_manager_with_mocks):
        """
        Test that invalid search term is rejected (edge case).
        Validates search term validation.
        """
        manager = inventory_manager_with_mocks
        
        # Mock validator to reject search term
        manager.validator.validate_search_term.return_value = (False, "Search term too short")
        
        with pytest.raises(InvalidProductDataError) as exc_info:
            manager.search_products("")
        
        assert "Invalid search term" in str(exc_info.value)
    
    def test_should_handle_database_failure_on_add(self, inventory_manager_with_mocks):
        """
        Test that database failure on add is handled properly (edge case).
        Validates error handling for database failures.
        """
        manager = inventory_manager_with_mocks
        
        # Mock validator responses
        manager.validator.validate_product_name.return_value = (True, None)
        manager.validator.validate_quantity.return_value = (True, None, 100)
        manager.validator.validate_price.return_value = (True, None, 49.99)
        
        # Mock database responses
        manager.db.fetch_one.return_value = None  # No duplicate
        manager.db.execute_query.return_value = False  # Database failure
        
        with pytest.raises(InvalidProductDataError) as exc_info:
            manager.add_product("Test Product", "100", "49.99")
        
        assert "Failed to add product" in str(exc_info.value)
    
    def test_should_update_multiple_fields_at_once(self, inventory_manager_with_mocks, sample_product_row):
        """
        Test updating multiple product fields simultaneously.
        Validates multi-field update functionality.
        """
        manager = inventory_manager_with_mocks
        
        # Mock validator responses
        manager.validator.validate_product_id.return_value = (True, None, 1)
        manager.validator.validate_quantity.return_value = (True, None, 200)
        manager.validator.validate_price.return_value = (True, None, 79.99)
        manager.validator.validate_product_name.return_value = (True, None)
        
        # Mock database responses
        updated_row = list(sample_product_row)
        updated_row[2] = 200  # Update quantity
        updated_row[3] = 79.99  # Update price
        updated_row[4] = "New Category"  # Update category
        manager.db.fetch_one.side_effect = [
            sample_product_row,  # Existing product
            tuple(updated_row)  # Updated product
        ]
        manager.db.execute_query.return_value = True
        
        product = manager.update_product("1", quantity="200", price="79.99", category="New Category")
        
        assert product.quantity == 200
        assert product.price == 79.99
        assert product.category == "New Category"
    
    def test_should_return_existing_product_when_no_updates(self, inventory_manager_with_mocks, sample_product_row):
        """
        Test that update returns existing product when no changes provided (edge case).
        Validates no-op update handling.
        """
        manager = inventory_manager_with_mocks
        
        # Mock validator responses
        manager.validator.validate_product_id.return_value = (True, None, 1)
        
        # Mock database response
        manager.db.fetch_one.return_value = sample_product_row
        
        product = manager.update_product("1")  # No updates provided
        
        assert product.id == 1
        assert product.name == "Test Product"

# Made with Bob
