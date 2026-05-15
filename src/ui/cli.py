"""
CLI Interface Module
Provides the command-line user interface for the Inventory Management System.
"""
import getpass
import sys
from typing import Optional, Dict, Any
from src.logic.inventory import (
    InventoryManager, 
    Product, 
    ProductNotFoundError, 
    DuplicateProductError, 
    InvalidProductDataError
)
from src.logic.auth import AuthenticationManager
from src.utils.validators import InputValidator
from src.utils.logger import AppLogger


class CLIInterface:
    """
    Command-line interface for the Inventory Management System.
    Handles user interaction, input validation, and formatted output.
    """
    
    def __init__(
        self,
        inventory_manager: InventoryManager,
        auth_manager: AuthenticationManager,
        validator: InputValidator,
        logger: Optional[AppLogger] = None
    ):
        """
        Initialize the CLI interface.
        
        Args:
            inventory_manager: InventoryManager instance for inventory operations
            auth_manager: AuthenticationManager instance for authentication
            validator: InputValidator instance for input validation
            logger: Optional AppLogger instance for logging
        """
        self.inventory = inventory_manager
        self.auth = auth_manager
        self.validator = validator
        self.logger = logger
        self.session: Optional[Dict[str, Any]] = None
        self.running = False
    
    def display_header(self) -> None:
        """Display the application header."""
        print("\n" + "=" * 60)
        print("INVENTORY MANAGEMENT SYSTEM v2.0")
        print("Refactored with Security & Best Practices")
        print("=" * 60)
    
    def display_menu(self) -> None:
        """Display the main menu options."""
        print("\n" + "=" * 60)
        print("MAIN MENU")
        print("=" * 60)
        print("1. Add Product")
        print("2. Update Product")
        print("3. Search Products")
        print("4. Delete Product")
        print("5. List All Products")
        print("6. Low Stock Report")
        print("7. Export Inventory")
        print("8. Logout")
        print("=" * 60)
    
    def display_separator(self, char: str = "-", length: int = 60) -> None:
        """Display a separator line."""
        print(char * length)
    
    def display_success(self, message: str) -> None:
        """Display a success message."""
        print(f"\n✓ SUCCESS: {message}")
    
    def display_error(self, message: str) -> None:
        """Display an error message."""
        print(f"\n✗ ERROR: {message}")
    
    def display_warning(self, message: str) -> None:
        """Display a warning message."""
        print(f"\n⚠ WARNING: {message}")
    
    def display_info(self, message: str) -> None:
        """Display an info message."""
        print(f"\nℹ INFO: {message}")
    
    def display_product_table(self, products: list[Product]) -> None:
        """
        Display products in a formatted table.
        
        Args:
            products: List of Product objects to display
        """
        if not products:
            print("\nNo products found.")
            return
        
        # Table header
        print("\n" + "=" * 100)
        print(f"{'ID':<6} {'Name':<30} {'Quantity':<12} {'Price':<12} {'Category':<20}")
        self.display_separator("=", 100)
        
        # Table rows
        for product in products:
            category = product.category if product.category else "N/A"
            print(f"{product.id:<6} {product.name:<30} {product.quantity:<12} ${product.price:<11.2f} {category:<20}")
        
        self.display_separator("=", 100)
        print(f"Total Products: {len(products)}")
    
    def get_input(self, prompt: str, allow_empty: bool = False) -> Optional[str]:
        """
        Get user input with optional empty check.
        
        Args:
            prompt: Input prompt to display
            allow_empty: Whether to allow empty input
            
        Returns:
            Optional[str]: User input or None if empty and not allowed
        """
        try:
            user_input = input(prompt).strip()
            if not user_input and not allow_empty:
                return None
            return user_input
        except (KeyboardInterrupt, EOFError):
            print("\n\nOperation cancelled by user.")
            return None
    
    def get_password(self, prompt: str = "Password: ") -> Optional[str]:
        """
        Get password input securely (hidden).
        
        Args:
            prompt: Password prompt to display
            
        Returns:
            Optional[str]: Password or None if cancelled
        """
        try:
            return getpass.getpass(prompt)
        except (KeyboardInterrupt, EOFError):
            print("\n\nOperation cancelled by user.")
            return None
    
    def confirm_action(self, prompt: str) -> bool:
        """
        Ask user for confirmation.
        
        Args:
            prompt: Confirmation prompt
            
        Returns:
            bool: True if confirmed, False otherwise
        """
        response = self.get_input(f"{prompt} (yes/no): ", allow_empty=False)
        return bool(response and response.lower() in ['yes', 'y'])
    
    def handle_login(self) -> bool:
        """
        Handle user login process.
        
        Returns:
            bool: True if login successful, False otherwise
        """
        print("\n" + "=" * 60)
        print("LOGIN")
        print("=" * 60)
        
        max_attempts = 3
        for attempt in range(max_attempts):
            username = self.get_input("Username: ")
            if not username:
                self.display_error("Username cannot be empty")
                continue
            
            # Validate username
            is_valid, error = self.validator.validate_username(username)
            if not is_valid:
                self.display_error(f"Invalid username: {error}")
                if self.logger:
                    self.logger.log_security_event('invalid_username', {'username': username, 'error': error or 'Unknown error'}, 'WARNING')
                continue
            
            password = self.get_password()
            if not password:
                self.display_error("Password cannot be empty")
                continue
            
            # Attempt login
            session = self.auth.login(username, password)
            
            if session:
                self.session = session
                self.display_success(f"Welcome, {username}!")
                if self.logger:
                    self.logger.log_security_event('login_success', {'username': username}, 'INFO')
                return True
            else:
                remaining = max_attempts - attempt - 1
                if remaining > 0:
                    self.display_error(f"Invalid credentials. {remaining} attempt(s) remaining.")
                else:
                    self.display_error("Maximum login attempts exceeded.")
                
                if self.logger:
                    self.logger.log_security_event('login_failed', {'username': username, 'reason': 'Invalid credentials'}, 'WARNING')
        
        return False
    
    def handle_add_product(self) -> None:
        """Handle adding a new product."""
        print("\n" + "=" * 60)
        print("ADD NEW PRODUCT")
        print("=" * 60)
        
        # Get product name
        name = self.get_input("Product Name: ")
        if not name:
            self.display_error("Product name cannot be empty")
            return
        
        # Get quantity
        quantity = self.get_input("Quantity: ")
        if not quantity:
            self.display_error("Quantity cannot be empty")
            return
        
        # Get price
        price = self.get_input("Price: ")
        if not price:
            self.display_error("Price cannot be empty")
            return
        
        # Get category (optional)
        category = self.get_input("Category (optional, press Enter to skip): ", allow_empty=True)
        if category == "":
            category = None
        
        try:
            # Add product
            product = self.inventory.add_product(name, quantity, price, category)
            self.display_success(f"Product added successfully! ID: {product.id}")
            
            # Display added product
            print("\nProduct Details:")
            self.display_product_table([product])
            
            if self.logger:
                self.logger.log_business_operation(
                    'add_product',
                    self.session['username'] if self.session else 'unknown',
                    {'product_id': product.id, 'name': product.name}
                )
        
        except InvalidProductDataError as e:
            self.display_error(str(e))
        except DuplicateProductError as e:
            self.display_error(str(e))
        except Exception as e:
            self.display_error(f"Failed to add product: {e}")
            if self.logger:
                self.logger.error(f"Error adding product: {e}", exc_info=True)
    
    def handle_update_product(self) -> None:
        """Handle updating an existing product."""
        print("\n" + "=" * 60)
        print("UPDATE PRODUCT")
        print("=" * 60)
        
        # Get product ID
        product_id = self.get_input("Product ID: ")
        if not product_id:
            self.display_error("Product ID cannot be empty")
            return
        
        try:
            # Check if product exists
            existing_product = self.inventory.get_product_by_id(product_id)
            
            print("\nCurrent Product Details:")
            self.display_product_table([existing_product])
            
            print("\nEnter new values (press Enter to keep current value):")
            
            # Get new quantity
            quantity = self.get_input(f"New Quantity (current: {existing_product.quantity}): ", allow_empty=True)
            if quantity == "":
                quantity = None
            
            # Get new price
            price = self.get_input(f"New Price (current: ${existing_product.price:.2f}): ", allow_empty=True)
            if price == "":
                price = None
            
            # Get new category
            current_category = existing_product.category if existing_product.category else "N/A"
            category = self.get_input(f"New Category (current: {current_category}): ", allow_empty=True)
            if category == "":
                category = None
            
            # Check if any updates provided
            if quantity is None and price is None and category is None:
                self.display_info("No updates provided. Product unchanged.")
                return
            
            # Update product
            updated_product = self.inventory.update_product(product_id, quantity, price, category)
            self.display_success("Product updated successfully!")
            
            # Display updated product
            print("\nUpdated Product Details:")
            self.display_product_table([updated_product])
            
            if self.logger:
                self.logger.log_business_operation(
                    'update_product',
                    self.session['username'] if self.session else 'unknown',
                    {'product_id': product_id}
                )
        
        except ProductNotFoundError as e:
            self.display_error(str(e))
        except InvalidProductDataError as e:
            self.display_error(str(e))
        except Exception as e:
            self.display_error(f"Failed to update product: {e}")
            if self.logger:
                self.logger.error(f"Error updating product: {e}", exc_info=True)
    
    def handle_search_products(self) -> None:
        """Handle searching for products."""
        print("\n" + "=" * 60)
        print("SEARCH PRODUCTS")
        print("=" * 60)
        
        search_term = self.get_input("Enter search term (name or category): ")
        if not search_term:
            self.display_error("Search term cannot be empty")
            return
        
        try:
            products = self.inventory.search_products(search_term)
            
            if products:
                print(f"\nFound {len(products)} product(s) matching '{search_term}':")
                self.display_product_table(products)
            else:
                self.display_info(f"No products found matching '{search_term}'")
            
            if self.logger:
                self.logger.debug(
                    f"Search performed",
                    {'search_term': search_term, 'results': len(products)}
                )
        
        except InvalidProductDataError as e:
            self.display_error(str(e))
        except Exception as e:
            self.display_error(f"Search failed: {e}")
            if self.logger:
                self.logger.error(f"Error searching products: {e}", exc_info=True)
    
    def handle_delete_product(self) -> None:
        """Handle deleting a product."""
        print("\n" + "=" * 60)
        print("DELETE PRODUCT")
        print("=" * 60)
        
        product_id = self.get_input("Product ID to delete: ")
        if not product_id:
            self.display_error("Product ID cannot be empty")
            return
        
        try:
            # Get product details before deletion
            product = self.inventory.get_product_by_id(product_id)
            
            print("\nProduct to be deleted:")
            self.display_product_table([product])
            
            # Confirm deletion
            if not self.confirm_action("\nAre you sure you want to delete this product?"):
                self.display_info("Deletion cancelled.")
                return
            
            # Delete product
            success = self.inventory.delete_product(product_id)
            
            if success:
                self.display_success(f"Product '{product.name}' (ID: {product_id}) deleted successfully!")
                
                if self.logger:
                    self.logger.log_business_operation(
                        'delete_product',
                        self.session['username'] if self.session else 'unknown',
                        {'product_id': product_id, 'name': product.name}
                    )
            else:
                self.display_error("Failed to delete product")
        
        except ProductNotFoundError as e:
            self.display_error(str(e))
        except InvalidProductDataError as e:
            self.display_error(str(e))
        except Exception as e:
            self.display_error(f"Failed to delete product: {e}")
            if self.logger:
                self.logger.error(f"Error deleting product: {e}", exc_info=True)
    
    def handle_list_products(self) -> None:
        """Handle listing all products."""
        print("\n" + "=" * 60)
        print("ALL PRODUCTS")
        print("=" * 60)
        
        try:
            products = self.inventory.get_all_products()
            
            if products:
                self.display_product_table(products)
                
                # Display inventory value
                total_value = self.inventory.get_inventory_value()
                print(f"\nTotal Inventory Value: ${total_value:,.2f}")
            else:
                self.display_info("No products in inventory")
        
        except Exception as e:
            self.display_error(f"Failed to list products: {e}")
            if self.logger:
                self.logger.error(f"Error listing products: {e}", exc_info=True)
    
    def handle_low_stock_report(self) -> None:
        """Handle generating low stock report."""
        print("\n" + "=" * 60)
        print("LOW STOCK REPORT")
        print("=" * 60)
        
        try:
            # Get low stock threshold from config or use default
            threshold = self.inventory.config.get_low_stock_threshold() if self.inventory.config else 5
            
            products = self.inventory.get_low_stock_products(threshold)
            
            if products:
                self.display_warning(f"The following products have stock below {threshold}:")
                self.display_product_table(products)
            else:
                self.display_success("All products are well stocked!")
            
            if self.logger:
                self.logger.info(
                    f"Low stock report generated",
                    {'threshold': threshold, 'low_stock_count': len(products)}
                )
        
        except Exception as e:
            self.display_error(f"Failed to generate low stock report: {e}")
            if self.logger:
                self.logger.error(f"Error generating low stock report: {e}", exc_info=True)
    
    def handle_export_inventory(self) -> None:
        """Handle exporting inventory to CSV."""
        print("\n" + "=" * 60)
        print("EXPORT INVENTORY")
        print("=" * 60)
        
        filename = self.get_input("Enter filename (e.g., inventory.csv): ")
        if not filename:
            self.display_error("Filename cannot be empty")
            return
        
        # Ensure .csv extension
        if not filename.endswith('.csv'):
            filename += '.csv'
        
        try:
            success = self.inventory.export_to_csv(filename)
            
            if success:
                self.display_success(f"Inventory exported to '{filename}' successfully!")
                
                if self.logger:
                    self.logger.log_business_operation(
                        'export_inventory',
                        self.session['username'] if self.session else 'unknown',
                        {'filename': filename}
                    )
            else:
                self.display_error("Failed to export inventory")
        
        except Exception as e:
            self.display_error(f"Export failed: {e}")
            if self.logger:
                self.logger.error(f"Error exporting inventory: {e}", exc_info=True)
    
    def handle_logout(self) -> bool:
        """
        Handle user logout.
        
        Returns:
            bool: True if logout successful
        """
        if self.session:
            username = self.session['username']
            session_id = self.session['session_id']
            
            if self.auth.logout(session_id):
                self.display_success(f"Goodbye, {username}!")
                
                if self.logger:
                    self.logger.log_security_event('logout', {'username': username}, 'INFO')
                
                self.session = None
                return True
            else:
                self.display_error("Logout failed")
                return False
        
        return True
    
    def run(self) -> None:
        """Main UI loop."""
        self.running = True
        
        # Display header
        self.display_header()
        
        # Handle login
        if not self.handle_login():
            self.display_error("Login failed. Exiting...")
            return
        
        # Main menu loop
        while self.running:
            try:
                # Check session validity
                if self.session and not self.auth.is_session_valid(self.session['session_id']):
                    self.display_warning("Session expired. Please login again.")
                    if self.handle_login():
                        continue
                    else:
                        break
                
                # Display menu
                self.display_menu()
                
                # Get user choice
                choice = self.get_input("\nEnter your choice (1-8): ")
                
                if not choice:
                    self.display_error("Invalid choice. Please try again.")
                    continue
                
                # Handle menu choice
                if choice == "1":
                    self.handle_add_product()
                elif choice == "2":
                    self.handle_update_product()
                elif choice == "3":
                    self.handle_search_products()
                elif choice == "4":
                    self.handle_delete_product()
                elif choice == "5":
                    self.handle_list_products()
                elif choice == "6":
                    self.handle_low_stock_report()
                elif choice == "7":
                    self.handle_export_inventory()
                elif choice == "8":
                    if self.handle_logout():
                        self.running = False
                else:
                    self.display_error("Invalid choice. Please enter a number between 1 and 8.")
            
            except KeyboardInterrupt:
                print("\n\nInterrupted by user. Logging out...")
                self.handle_logout()
                self.running = False
            except Exception as e:
                self.display_error(f"An unexpected error occurred: {e}")
                if self.logger:
                    self.logger.error(f"Unexpected error in main loop: {e}", exc_info=True)
        
        # Cleanup
        print("\n" + "=" * 60)
        print("Thank you for using Inventory Management System!")
        print("=" * 60 + "\n")


# Made with Bob