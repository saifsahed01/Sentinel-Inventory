"""
Inventory Management Business Logic Module
Implements OOP design for inventory operations with proper validation and security.
"""
import csv
from datetime import datetime
from typing import Optional, List, Dict, Any
from src.data.database import DatabaseManager
from src.utils.validators import InputValidator, ValidationError
from src.utils.logger import AppLogger
from src.utils.config import Config


# Custom Exceptions
class ProductNotFoundError(Exception):
    """Raised when a product is not found in the inventory."""
    pass


class DuplicateProductError(Exception):
    """Raised when attempting to add a product that already exists."""
    pass


class InvalidProductDataError(Exception):
    """Raised when product data fails validation."""
    pass


class Product:
    """
    Represents a product in the inventory system.
    Encapsulates product data with validation and serialization methods.
    """
    
    def __init__(
        self,
        name: str,
        quantity: int,
        price: float,
        category: Optional[str] = None,
        product_id: Optional[int] = None,
        created_at: Optional[str] = None,
        updated_at: Optional[str] = None
    ):
        """
        Initialize a Product instance with validation.
        
        Args:
            name: Product name
            quantity: Product quantity (must be non-negative)
            price: Product price (must be positive)
            category: Optional product category
            product_id: Optional product ID (set by database)
            created_at: Optional creation timestamp
            updated_at: Optional last update timestamp
            
        Raises:
            InvalidProductDataError: If validation fails
        """
        # Validate name
        is_valid, error = InputValidator.validate_product_name(name)
        if not is_valid:
            raise InvalidProductDataError(f"Invalid product name: {error}")
        
        # Validate quantity
        if quantity < 0:
            raise InvalidProductDataError("Quantity cannot be negative")
        
        # Validate price
        if price < 0:
            raise InvalidProductDataError("Price cannot be negative")
        
        # Validate category if provided
        if category is not None:
            is_valid, error = InputValidator.validate_product_name(category)
            if not is_valid:
                raise InvalidProductDataError(f"Invalid category: {error}")
        
        self.id = product_id
        self.name = name.strip()
        self.quantity = quantity
        self.price = round(price, 2)
        self.category = category.strip() if category else None
        self.created_at = created_at
        self.updated_at = updated_at or datetime.now().isoformat()
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert product to dictionary representation.
        
        Returns:
            Dict[str, Any]: Product data as dictionary
        """
        return {
            'id': self.id,
            'name': self.name,
            'quantity': self.quantity,
            'price': self.price,
            'category': self.category,
            'created_at': self.created_at,
            'updated_at': self.updated_at
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Product':
        """
        Create a Product instance from a dictionary.
        
        Args:
            data: Dictionary containing product data
            
        Returns:
            Product: New Product instance
        """
        return cls(
            name=data['name'],
            quantity=data['quantity'],
            price=data['price'],
            category=data.get('category'),
            product_id=data.get('id'),
            created_at=data.get('created_at'),
            updated_at=data.get('updated_at')
        )
    
    @classmethod
    def from_db_row(cls, row: tuple) -> 'Product':
        """
        Create a Product instance from a database row.
        
        Args:
            row: Database row tuple (id, name, quantity, price, category, created_at, updated_at)
            
        Returns:
            Product: New Product instance
        """
        # Handle both old schema (4 columns) and new schema (7 columns)
        if len(row) == 4:
            return cls(
                product_id=row[0],
                name=row[1],
                quantity=row[2],
                price=row[3],
                category=None,
                created_at=None,
                updated_at=None
            )
        else:
            return cls(
                product_id=row[0],
                name=row[1],
                quantity=row[2],
                price=row[3],
                category=row[4] if len(row) > 4 else None,
                created_at=row[5] if len(row) > 5 else None,
                updated_at=row[6] if len(row) > 6 else None
            )
    
    def __str__(self) -> str:
        """String representation of the product."""
        return f"Product(id={self.id}, name='{self.name}', quantity={self.quantity}, price=${self.price:.2f})"
    
    def __repr__(self) -> str:
        """Developer-friendly representation of the product."""
        return (f"Product(id={self.id}, name='{self.name}', quantity={self.quantity}, "
                f"price={self.price}, category='{self.category}')")


class InventoryManager:
    """
    Manages inventory operations with business logic and validation.
    Integrates with DatabaseManager, InputValidator, and AppLogger.
    """
    
    def __init__(
        self,
        db_manager: DatabaseManager,
        validator: InputValidator,
        logger: Optional[AppLogger] = None,
        config: Optional[Config] = None
    ):
        """
        Initialize the InventoryManager.
        
        Args:
            db_manager: DatabaseManager instance for database operations
            validator: InputValidator instance for input validation
            logger: Optional AppLogger instance for logging
            config: Optional Config instance for configuration
        """
        self.db = db_manager
        self.validator = validator
        self.logger = logger
        self.config = config
        self._ensure_schema()
    
    def _ensure_schema(self) -> None:
        """
        Ensure the products table has the correct schema.
        Adds category column if it doesn't exist (for legacy database compatibility).
        """
        try:
            # Check if category column exists
            result = self.db.fetch_one("PRAGMA table_info(products)", ())
            if result:
                # Get column names
                columns = self.db.fetch_all("PRAGMA table_info(products)", ())
                column_names = [col[1] for col in columns]
                
                # Add category column if missing
                if 'category' not in column_names:
                    self.db.execute_query(
                        "ALTER TABLE products ADD COLUMN category TEXT",
                        ()
                    )
                    if self.logger:
                        self.logger.info("Added category column to products table")
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error ensuring schema: {e}", exc_info=True)
    
    def add_product(
        self,
        name: str,
        quantity: str,
        price: str,
        category: Optional[str] = None
    ) -> Product:
        """
        Add a new product to the inventory.
        
        Args:
            name: Product name
            quantity: Product quantity as string
            price: Product price as string
            category: Optional product category
            
        Returns:
            Product: The newly created product
            
        Raises:
            InvalidProductDataError: If validation fails
            DuplicateProductError: If product name already exists
        """
        # Validate inputs
        is_valid, error = self.validator.validate_product_name(name)
        if not is_valid:
            error_msg = error or "Invalid product name"
            if self.logger:
                self.logger.log_validation_error('name', name, error_msg)
            raise InvalidProductDataError(f"Invalid product name: {error_msg}")
        
        is_valid, error, qty = self.validator.validate_quantity(quantity)
        if not is_valid:
            error_msg = error or "Invalid quantity"
            if self.logger:
                self.logger.log_validation_error('quantity', quantity, error_msg)
            raise InvalidProductDataError(f"Invalid quantity: {error_msg}")
        
        is_valid, error, price_val = self.validator.validate_price(price)
        if not is_valid:
            error_msg = error or "Invalid price"
            if self.logger:
                self.logger.log_validation_error('price', price, error_msg)
            raise InvalidProductDataError(f"Invalid price: {error_msg}")
        
        # Validate category if provided
        if category:
            is_valid, error = self.validator.validate_product_name(category)
            if not is_valid:
                error_msg = error or "Invalid category"
                if self.logger:
                    self.logger.log_validation_error('category', category, error_msg)
                raise InvalidProductDataError(f"Invalid category: {error_msg}")
        
        # Check for duplicate product name
        existing = self.db.fetch_one(
            "SELECT id FROM products WHERE LOWER(name) = LOWER(?)",
            (name.strip(),)
        )
        if existing:
            error_msg = f"Product with name '{name}' already exists"
            if self.logger:
                self.logger.warning(error_msg, {'name': name})
            raise DuplicateProductError(error_msg)
        
        # Insert product into database
        query = """
            INSERT INTO products (name, quantity, price, category, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """
        timestamp = datetime.now().isoformat()
        success = self.db.execute_query(
            query,
            (name.strip(), qty, price_val, category.strip() if category else None, timestamp, timestamp)
        )
        
        if not success:
            error_msg = "Failed to add product to database"
            if self.logger:
                self.logger.error(error_msg, {'name': name})
            raise InvalidProductDataError(error_msg)
        
        # Retrieve the newly created product
        product_row = self.db.fetch_one(
            "SELECT id, name, quantity, price, category, created_at, updated_at FROM products WHERE name = ?",
            (name.strip(),)
        )
        
        if not product_row:
            raise InvalidProductDataError("Failed to retrieve newly created product")
        
        product = Product.from_db_row(product_row)
        
        if self.logger:
            self.logger.log_business_operation(
                'add_product',
                'system',
                {'product_id': product.id, 'name': product.name, 'quantity': qty, 'price': price_val}
            )
        
        return product
    
    def update_product(
        self,
        product_id: str,
        quantity: Optional[str] = None,
        price: Optional[str] = None,
        category: Optional[str] = None
    ) -> Product:
        """
        Update an existing product's quantity, price, or category.
        
        Args:
            product_id: Product ID as string
            quantity: Optional new quantity as string
            price: Optional new price as string
            category: Optional new category
            
        Returns:
            Product: The updated product
            
        Raises:
            InvalidProductDataError: If validation fails
            ProductNotFoundError: If product doesn't exist
        """
        # Validate product ID
        is_valid, error, pid = self.validator.validate_product_id(product_id)
        if not is_valid:
            error_msg = error or "Invalid product ID"
            if self.logger:
                self.logger.log_validation_error('product_id', product_id, error_msg)
            raise InvalidProductDataError(f"Invalid product ID: {error_msg}")
        
        # Check if product exists
        existing = self.db.fetch_one(
            "SELECT id, name, quantity, price, category, created_at, updated_at FROM products WHERE id = ?",
            (pid,)
        )
        if not existing:
            error_msg = f"Product with ID {pid} not found"
            if self.logger:
                self.logger.warning(error_msg, {'product_id': pid})
            raise ProductNotFoundError(error_msg)
        
        # Build update query dynamically based on provided parameters
        updates = []
        params = []
        
        if quantity is not None:
            is_valid, error, qty = self.validator.validate_quantity(quantity)
            if not is_valid:
                error_msg = error or "Invalid quantity"
                if self.logger:
                    self.logger.log_validation_error('quantity', quantity, error_msg)
                raise InvalidProductDataError(f"Invalid quantity: {error_msg}")
            updates.append("quantity = ?")
            params.append(qty)
        
        if price is not None:
            is_valid, error, price_val = self.validator.validate_price(price)
            if not is_valid:
                error_msg = error or "Invalid price"
                if self.logger:
                    self.logger.log_validation_error('price', price, error_msg)
                raise InvalidProductDataError(f"Invalid price: {error_msg}")
            updates.append("price = ?")
            params.append(price_val)
        
        if category is not None:
            is_valid, error = self.validator.validate_product_name(category)
            if not is_valid:
                error_msg = error or "Invalid category"
                if self.logger:
                    self.logger.log_validation_error('category', category, error_msg)
                raise InvalidProductDataError(f"Invalid category: {error_msg}")
            updates.append("category = ?")
            params.append(category.strip())
        
        if not updates:
            # Nothing to update, return existing product
            return Product.from_db_row(existing)
        
        # Add updated_at timestamp
        updates.append("updated_at = ?")
        params.append(datetime.now().isoformat())
        
        # Add product ID to params
        params.append(pid)
        
        # Execute update
        query = f"UPDATE products SET {', '.join(updates)} WHERE id = ?"
        success = self.db.execute_query(query, tuple(params))
        
        if not success:
            error_msg = "Failed to update product"
            if self.logger:
                self.logger.error(error_msg, {'product_id': pid})
            raise InvalidProductDataError(error_msg)
        
        # Retrieve updated product
        updated_row = self.db.fetch_one(
            "SELECT id, name, quantity, price, category, created_at, updated_at FROM products WHERE id = ?",
            (pid,)
        )
        
        if not updated_row:
            raise InvalidProductDataError("Failed to retrieve updated product")
        
        product = Product.from_db_row(updated_row)
        
        if self.logger:
            self.logger.log_business_operation(
                'update_product',
                'system',
                {'product_id': pid, 'updates': updates}
            )
        
        return product
    
    def delete_product(self, product_id: str) -> bool:
        """
        Delete a product from the inventory.
        
        Args:
            product_id: Product ID as string
            
        Returns:
            bool: True if deletion successful
            
        Raises:
            InvalidProductDataError: If validation fails
            ProductNotFoundError: If product doesn't exist
        """
        # Validate product ID
        is_valid, error, pid = self.validator.validate_product_id(product_id)
        if not is_valid:
            error_msg = error or "Invalid product ID"
            if self.logger:
                self.logger.log_validation_error('product_id', product_id, error_msg)
            raise InvalidProductDataError(f"Invalid product ID: {error_msg}")
        
        # Check if product exists
        existing = self.db.fetch_one(
            "SELECT name FROM products WHERE id = ?",
            (pid,)
        )
        if not existing:
            error_msg = f"Product with ID {pid} not found"
            if self.logger:
                self.logger.warning(error_msg, {'product_id': pid})
            raise ProductNotFoundError(error_msg)
        
        # Delete product
        success = self.db.execute_query(
            "DELETE FROM products WHERE id = ?",
            (pid,)
        )
        
        if not success:
            error_msg = "Failed to delete product"
            if self.logger:
                self.logger.error(error_msg, {'product_id': pid})
            return False
        
        if self.logger:
            self.logger.log_business_operation(
                'delete_product',
                'system',
                {'product_id': pid, 'name': existing[0]}
            )
        
        return True
    
    def search_products(self, search_term: str) -> List[Product]:
        """
        Search for products by name or category.
        
        Args:
            search_term: Search term (name or category)
            
        Returns:
            List[Product]: List of matching products
            
        Raises:
            InvalidProductDataError: If validation fails
        """
        # Validate search term
        is_valid, error = self.validator.validate_search_term(search_term)
        if not is_valid:
            error_msg = error or "Invalid search term"
            if self.logger:
                self.logger.log_validation_error('search_term', search_term, error_msg)
            raise InvalidProductDataError(f"Invalid search term: {error_msg}")
        
        # Search in name and category
        query = """
            SELECT id, name, quantity, price, category, created_at, updated_at
            FROM products
            WHERE LOWER(name) LIKE LOWER(?) OR LOWER(category) LIKE LOWER(?)
            ORDER BY name
        """
        search_pattern = f"%{search_term.strip()}%"
        rows = self.db.fetch_all(query, (search_pattern, search_pattern))
        
        products = [Product.from_db_row(row) for row in rows]
        
        if self.logger:
            self.logger.debug(
                f"Search completed",
                {'search_term': search_term, 'results_count': len(products)}
            )
        
        return products
    
    def get_product_by_id(self, product_id: str) -> Product:
        """
        Get a single product by ID.
        
        Args:
            product_id: Product ID as string
            
        Returns:
            Product: The requested product
            
        Raises:
            InvalidProductDataError: If validation fails
            ProductNotFoundError: If product doesn't exist
        """
        # Validate product ID
        is_valid, error, pid = self.validator.validate_product_id(product_id)
        if not is_valid:
            error_msg = error or "Invalid product ID"
            if self.logger:
                self.logger.log_validation_error('product_id', product_id, error_msg)
            raise InvalidProductDataError(f"Invalid product ID: {error_msg}")
        
        # Fetch product
        row = self.db.fetch_one(
            "SELECT id, name, quantity, price, category, created_at, updated_at FROM products WHERE id = ?",
            (pid,)
        )
        
        if not row:
            error_msg = f"Product with ID {pid} not found"
            if self.logger:
                self.logger.warning(error_msg, {'product_id': pid})
            raise ProductNotFoundError(error_msg)
        
        return Product.from_db_row(row)
    
    def get_all_products(self) -> List[Product]:
        """
        Get all products in the inventory.
        
        Returns:
            List[Product]: List of all products
        """
        rows = self.db.fetch_all(
            "SELECT id, name, quantity, price, category, created_at, updated_at FROM products ORDER BY name",
            ()
        )
        
        products = [Product.from_db_row(row) for row in rows]
        
        if self.logger:
            self.logger.debug(f"Retrieved all products", {'count': len(products)})
        
        return products
    
    def get_low_stock_products(self, threshold: Optional[int] = None) -> List[Product]:
        """
        Get products with quantity below the threshold.
        
        Args:
            threshold: Optional stock threshold (uses config default if not provided)
            
        Returns:
            List[Product]: List of low stock products
        """
        if threshold is None:
            threshold = self.config.get_low_stock_threshold() if self.config else 10
        
        rows = self.db.fetch_all(
            "SELECT id, name, quantity, price, category, created_at, updated_at FROM products WHERE quantity < ? ORDER BY quantity ASC",
            (threshold,)
        )
        
        products = [Product.from_db_row(row) for row in rows]
        
        if self.logger:
            self.logger.info(
                f"Low stock report generated",
                {'threshold': threshold, 'low_stock_count': len(products)}
            )
        
        return products
    
    def get_inventory_value(self) -> float:
        """
        Calculate the total value of all inventory.
        
        Returns:
            float: Total inventory value
        """
        result = self.db.fetch_one(
            "SELECT SUM(quantity * price) FROM products",
            ()
        )
        
        total_value = result[0] if result and result[0] is not None else 0.0
        
        if self.logger:
            self.logger.debug(f"Inventory value calculated", {'total_value': total_value})
        
        return round(total_value, 2)
    
    def export_to_csv(self, filename: str) -> bool:
        """
        Export inventory to a CSV file.
        
        Args:
            filename: Path to the CSV file
            
        Returns:
            bool: True if export successful
        """
        try:
            products = self.get_all_products()
            
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                fieldnames = ['id', 'name', 'quantity', 'price', 'category', 'created_at', 'updated_at']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                
                writer.writeheader()
                for product in products:
                    writer.writerow(product.to_dict())
            
            if self.logger:
                self.logger.info(
                    f"Inventory exported to CSV",
                    {'filename': filename, 'product_count': len(products)}
                )
            
            return True
        except Exception as e:
            if self.logger:
                self.logger.error(f"Failed to export inventory: {e}", exc_info=True)
            return False


# Made with Bob