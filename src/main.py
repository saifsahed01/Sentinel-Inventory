"""
Main Entry Point for Inventory Management System
Initializes all components and starts the CLI interface.
Also exposes Flask app instance for web deployment (e.g., Vercel).
"""
import sys
import os
from typing import Optional

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.utils.config import Config
from src.utils.logger import AppLogger
from src.utils.validators import InputValidator
from src.data.database import DatabaseManager
from src.logic.auth import AuthenticationManager
from src.logic.inventory import InventoryManager
from src.ui.cli import CLIInterface

# Import Flask app for web deployment (Vercel, etc.)
from src.web.app import create_app

# Create Flask app instance for web deployment
# This is required by Vercel and other WSGI servers
app = create_app()


def initialize_application() -> tuple[Config, AppLogger, DatabaseManager, InputValidator, AuthenticationManager, InventoryManager, CLIInterface]:
    """
    Initialize all application components in the correct order.
    
    Returns:
        tuple: All initialized components
        
    Raises:
        Exception: If initialization fails
    """
    print("Initializing Inventory Management System...")
    
    # 1. Load Configuration
    print("Loading configuration...")
    config = Config()
    
    # 2. Initialize Logger
    print("Setting up logging...")
    logger = AppLogger(
        name=config.APP_NAME,
        log_dir=config.get_log_directory()
    )
    logger.info("Application starting", {'version': config.APP_VERSION})
    
    # 3. Initialize Database Manager
    print("Connecting to database...")
    db_manager = DatabaseManager(db_path=config.get_database_path())
    
    # Connect to database
    if not db_manager.connect():
        raise Exception("Failed to connect to database")
    
    # Initialize database schema
    if not db_manager.initialize_database():
        raise Exception("Failed to initialize database")
    
    logger.info("Database initialized successfully")
    
    # 4. Create Input Validator
    print("Setting up input validation...")
    validator = InputValidator()
    
    # 5. Initialize Authentication Manager
    print("Setting up authentication...")
    auth_manager = AuthenticationManager(db_manager)
    
    # 6. Initialize Inventory Manager
    print("Setting up inventory management...")
    inventory_manager = InventoryManager(
        db_manager=db_manager,
        validator=validator,
        logger=logger,
        config=config
    )
    
    # 7. Create CLI Interface
    print("Setting up user interface...")
    cli = CLIInterface(
        inventory_manager=inventory_manager,
        auth_manager=auth_manager,
        validator=validator,
        logger=logger
    )
    
    logger.info("Application initialized successfully")
    print("Initialization complete!\n")
    
    return config, logger, db_manager, validator, auth_manager, inventory_manager, cli


def cleanup(db_manager: Optional[DatabaseManager], logger: Optional[AppLogger]) -> None:
    """
    Cleanup resources before exit.
    
    Args:
        db_manager: DatabaseManager instance to close
        logger: AppLogger instance for logging
    """
    try:
        if db_manager:
            print("\nClosing database connection...")
            db_manager.close()
        
        if logger:
            logger.info("Application shutdown complete")
    except Exception as e:
        print(f"Error during cleanup: {e}")


def main() -> int:
    """
    Main application entry point.
    
    Returns:
        int: Exit code (0 for success, 1 for error)
    """
    config: Optional[Config] = None
    logger: Optional[AppLogger] = None
    db_manager: Optional[DatabaseManager] = None
    
    try:
        # Initialize all components
        config, logger, db_manager, validator, auth_manager, inventory_manager, cli = initialize_application()
        
        # Run the CLI interface
        cli.run()
        
        # Normal exit
        return 0
    
    except KeyboardInterrupt:
        print("\n\nApplication interrupted by user.")
        if logger:
            logger.warning("Application interrupted by user")
        return 0
    
    except Exception as e:
        print(f"\n✗ FATAL ERROR: {e}")
        if logger:
            logger.critical(f"Fatal error: {e}", exc_info=True)
        else:
            # If logger not initialized, print traceback
            import traceback
            traceback.print_exc()
        return 1
    
    finally:
        # Cleanup resources
        cleanup(db_manager, logger)


if __name__ == "__main__":
    """
    Entry point when script is run directly.
    """
    exit_code = main()
    sys.exit(exit_code)


# Made with Bob