"""
Flask Application Factory
Creates and configures the Flask application with all necessary components.
"""
import os
import secrets
from flask import Flask
from src.data.database import DatabaseManager
from src.logic.auth import AuthenticationManager
from src.logic.inventory import InventoryManager
from src.utils.validators import InputValidator
from src.utils.logger import AppLogger
from src.utils.config import Config


def create_app(config_path: str = ".env") -> Flask:
    """
    Create and configure the Flask application.
    
    Args:
        config_path: Path to configuration file
        
    Returns:
        Flask: Configured Flask application instance
    """
    app = Flask(__name__)
    
    try:
        # Load configuration
        config = Config(config_path)
        
        # Configure Flask secret key
        app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY', secrets.token_hex(32))
        
        # Session configuration
        app.config['SESSION_COOKIE_SECURE'] = not config.is_debug_mode()  # True in production
        app.config['SESSION_COOKIE_HTTPONLY'] = True
        app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
        app.config['PERMANENT_SESSION_LIFETIME'] = config.get_session_timeout() * 60  # Convert to seconds
        
        # Initialize database with error handling for serverless
        db_path = config.get_database_path()
        print(f"Initializing database at: {db_path}")
        db_manager = DatabaseManager(db_path)
        
        if not db_manager.connect():
            raise RuntimeError(f"Failed to connect to database at {db_path}")
        
        if not db_manager.initialize_database():
            raise RuntimeError("Failed to initialize database schema")
        
        # Initialize managers
        auth_manager = AuthenticationManager(db_manager)
        validator = InputValidator()
        
        # Initialize logger with error handling
        log_dir = config.get_log_directory()
        print(f"Initializing logger with directory: {log_dir}")
        logger = AppLogger(config.get_log_directory())
        
        inventory_manager = InventoryManager(db_manager, validator, logger, config)
        
        # Store managers in app config for access in routes
        app.config['DB_MANAGER'] = db_manager
        app.config['AUTH_MANAGER'] = auth_manager
        app.config['INVENTORY_MANAGER'] = inventory_manager
        app.config['LOGGER'] = logger
        app.config['APP_CONFIG'] = config
        
        print("Flask app initialization successful")
        
    except Exception as e:
        print(f"CRITICAL ERROR during app initialization: {e}")
        import traceback
        traceback.print_exc()
        # Re-raise to make the error visible in Vercel logs
        raise
    
    # Register error handlers
    @app.errorhandler(404)
    def not_found_error(error):
        """Handle 404 errors."""
        from flask import render_template
        return render_template('error.html', 
                             error_code=404, 
                             error_message="Page not found"), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        """Handle 500 errors."""
        from flask import render_template
        # Safely log error if logger is available
        if 'LOGGER' in app.config:
            app.config['LOGGER'].error(f"Internal server error: {error}", exc_info=True)
        else:
            print(f"Internal server error: {error}")
            import traceback
            traceback.print_exc()
        return render_template('error.html',
                             error_code=500,
                             error_message="Internal server error"), 500
    
    # Register blueprints
    from src.web.routes.auth import auth_bp
    from src.web.routes.inventory import inventory_bp
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(inventory_bp)
    
    # Cleanup on shutdown
    @app.teardown_appcontext
    def shutdown_session(exception=None):
        """Clean up resources on application shutdown."""
        pass  # Database connection will be managed by the app
    
    return app


if __name__ == '__main__':
    """Run the Flask application in development mode."""
    app = create_app()
    config = app.config['APP_CONFIG']
    app.run(
        debug=config.is_debug_mode(),
        host='0.0.0.0',
        port=5000
    )

# Made with Bob
