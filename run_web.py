"""
Web Server Entry Point

This module serves as the entry point for the Flask web application.
It creates and runs the Flask app instance with appropriate configuration.

Usage:
    python run_web.py

The server will start on http://0.0.0.0:5000 by default.
"""

from src.web.app import create_app

if __name__ == "__main__":
    # Create Flask application instance
    app = create_app()
    
    # Run the development server
    # Host 0.0.0.0 makes the server accessible from other machines
    # Port 5000 is the default Flask development port
    # Debug mode is controlled by the app's configuration
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=app.config.get("DEBUG", False)
    )

# Made with Bob
